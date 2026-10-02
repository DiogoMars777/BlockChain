from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.cu019_envios_logisticos.shipment import Envio
from app.models.cu020_asignacion_unidades_envio.shipment_unit import EnvioUnidad
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu005_bitacora.bitacora import Bitacora
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.controllers.shared import get_bolivia_now, get_client_ip, require_roles
from app.views.cu020_asignacion_unidades_envio.shipment_unit_views import (
    EnvioUnidadesResponse,
    EnvioUnidadAsignadaResponse,
    EnvioUnidadCandidateResponse,
    EnvioUnidadAssignRequest,
    EnvioUnidadBulkAssignRequest,
    EnvioUnidadActionResponse
)

router = APIRouter(prefix="/shipments", tags=["Asignar / Desasignar Unidades a Envio (CU-020)"])

# Solo los Envios en preparacion pueden recibir o devolver unidades: una vez
# despachado, el contenido del envio es inmutable.
ESTADOS_ASIGNABLES = {"preparacion"}

ROLES_GESTION_ENVIO = ("SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones")

requires_shipment_management = require_roles(*ROLES_GESTION_ENVIO)


class ShipmentUnitController:

    @staticmethod
    def _tenant_id(current_user: User) -> int:
        """Empresa activa del token. Nunca se cae a un tenant por defecto."""
        idtenant = getattr(getattr(current_user, "tenant", None), "idtenant", None)
        if idtenant is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no tiene una empresa activa asignada."
            )
        return idtenant

    @staticmethod
    def _get_envio_or_404(db: Session, current_user: User, idenvio: int) -> Envio:
        envio = db.execute(
            select(Envio).where(
                Envio.idenvio == idenvio,
                Envio.idtenant == ShipmentUnitController._tenant_id(current_user)
            )
        ).scalar_one_or_none()
        if not envio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Envio con ID {idenvio} no encontrado o no pertenece a la empresa."
            )
        return envio

    @staticmethod
    def _get_idusuariotenant(db: Session, current_user: User, tenant_id: int):
        stmt_ut = select(UsuarioTenant.idusuariotenant).where(
            UsuarioTenant.idusuario == current_user.idusuario,
            UsuarioTenant.idtenant == tenant_id
        )
        idut = db.execute(stmt_ut).scalar()
        if not idut:
            idut = db.execute(
                select(UsuarioTenant.idusuariotenant).where(
                    UsuarioTenant.idusuario == current_user.idusuario
                )
            ).scalar()
        return idut

    @staticmethod
    def _auditar(db: Session, current_user: User, tenant_id: int, request: Request, accion: str, idenvio: int) -> None:
        idut = ShipmentUnitController._get_idusuariotenant(db, current_user, tenant_id)
        if idut:
            db.add(Bitacora(
                idusuariotenant=idut,
                accion=accion,
                entidad="EnvioUnidad",
                identidad=idenvio,
                ip=get_client_ip(request),
                fechahora=get_bolivia_now()
            ))

    @staticmethod
    def _consulta_unidades(ids_unidad: List[int]):
        """Une el vinculo de asignacion con los datos de producto de cada unidad."""
        return (
            select(EnvioUnidad.idenviounidad, UnidadProducto.idunidad, UnidadProducto.numeroserie,
                   UnidadProducto.idvariante, UnidadProducto.estado, UnidadProducto.idrecepciondetalle,
                   VarianteProducto.sku, Producto.nombre)
            .join(UnidadProducto, EnvioUnidad.idunidad == UnidadProducto.idunidad)
            .join(VarianteProducto, UnidadProducto.idvariante == VarianteProducto.idvariante)
            .join(Producto, VarianteProducto.idproducto == Producto.idproducto)
            .where(EnvioUnidad.idunidad.in_(ids_unidad))
            .order_by(UnidadProducto.numeroserie)
        )

    @staticmethod
    def _asignadas(db: Session, idenvio: int) -> List[EnvioUnidadAsignadaResponse]:
        ids_unidad = db.execute(
            select(UnidadProducto.idunidad)
            .join(EnvioUnidad, EnvioUnidad.idunidad == UnidadProducto.idunidad)
            .where(EnvioUnidad.idenvio == idenvio)
        ).scalars().all()

        if not ids_unidad:
            return []

        filas = db.execute(ShipmentUnitController._consulta_unidades(ids_unidad)).all()
        return [
            EnvioUnidadAsignadaResponse(
                idenviounidad=f.idenviounidad,
                idunidad=f.idunidad,
                numeroserie=f.numeroserie,
                idvariante=f.idvariante,
                sku=f.sku,
                producto_nombre=f.nombre,
                estado=str(f.estado) if f.estado else None,
                idrecepciondetalle=f.idrecepciondetalle
            )
            for f in filas
        ]

    @staticmethod
    def _disponibles(db: Session, tenant_id: int) -> List[EnvioUnidadCandidateResponse]:
        # Candidatas: unidades del tenant en estado 'disponible' que no estan
        # asignadas a ningun envio, incluido este (las suyas van en 'asignadas').
        filas = db.execute(
            select(UnidadProducto.idunidad, UnidadProducto.numeroserie, UnidadProducto.idvariante,
                   UnidadProducto.estado, UnidadProducto.idrecepciondetalle, VarianteProducto.sku,
                   Producto.nombre)
            .join(VarianteProducto, UnidadProducto.idvariante == VarianteProducto.idvariante)
            .join(Producto, VarianteProducto.idproducto == Producto.idproducto)
            .where(
                UnidadProducto.idtenant == tenant_id,
                UnidadProducto.estado == "disponible",
                ~UnidadProducto.idunidad.in_(select(EnvioUnidad.idunidad))
            )
            .order_by(UnidadProducto.numeroserie)
            .limit(200)
        ).all()
        return [
            EnvioUnidadCandidateResponse(
                idunidad=f.idunidad,
                numeroserie=f.numeroserie,
                idvariante=f.idvariante,
                sku=f.sku,
                producto_nombre=f.nombre,
                estado=str(f.estado) if f.estado else None,
                idrecepciondetalle=f.idrecepciondetalle
            )
            for f in filas
        ]

    @staticmethod
    def list_unidades(db: Session, current_user: User, idenvio: int) -> EnvioUnidadesResponse:
        envio = ShipmentUnitController._get_envio_or_404(db, current_user, idenvio)
        asignadas = ShipmentUnitController._asignadas(db, envio.idenvio)
        return EnvioUnidadesResponse(
            idenvio=envio.idenvio,
            codigoenvio=envio.codigoenvio,
            estado=str(envio.estado),
            asignadas=asignadas,
            disponibles=ShipmentUnitController._disponibles(
                db, envio.idtenant
            )
        )

    @staticmethod
    def _validar_envio_asignable(envio: Envio) -> None:
        if str(envio.estado).lower() not in ESTADOS_ASIGNABLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se pueden asignar o desasignar unidades en envios en estado "
                       f"'preparacion'. El estado actual es '{envio.estado}'."
            )

    @staticmethod
    def _preparar_asignacion(db: Session, envio: Envio, tenant_id: int, idunidad: int) -> UnidadProducto:
        unidad = db.execute(
            select(UnidadProducto).where(
                UnidadProducto.idunidad == idunidad,
                UnidadProducto.idtenant == tenant_id
            )
        ).scalar_one_or_none()

        if not unidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unidad con ID {idunidad} no encontrada o no pertenece a la empresa."
            )

        duplicada = db.execute(
            select(EnvioUnidad).where(
                EnvioUnidad.idenvio == envio.idenvio,
                EnvioUnidad.idunidad == idunidad
            )
        ).scalar_one_or_none()

        if duplicada:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La unidad {unidad.numeroserie} ya esta asignada al envio {envio.codigoenvio}."
            )

        otro_envio = db.execute(
            select(Envio).join(
                EnvioUnidad, EnvioUnidad.idenvio == Envio.idenvio
            ).where(
                EnvioUnidad.idunidad == idunidad,
                Envio.idenvio != envio.idenvio,
                Envio.idtenant == tenant_id,
                Envio.estado != "cancelado"
            )
        ).scalar_one_or_none()

        if otro_envio:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La unidad {unidad.numeroserie} ya esta asignada al envio {otro_envio.codigoenvio}."
            )

        if str(unidad.estado).lower() != "disponible":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La unidad {unidad.numeroserie} esta en estado '{unidad.estado}' "
                       f"y solo puede asignarse a un envio si esta 'disponible'."
            )

        return unidad

    @staticmethod
    def assign_unit(
        db: Session,
        current_user: User,
        request: Request,
        idenvio: int,
        body: EnvioUnidadAssignRequest
    ) -> EnvioUnidadActionResponse:
        envio = ShipmentUnitController._get_envio_or_404(db, current_user, idenvio)
        ShipmentUnitController._validar_envio_asignable(envio)

        unidad = ShipmentUnitController._preparar_asignacion(db, envio, envio.idtenant, body.idunidad)

        db.add(EnvioUnidad(idenvio=envio.idenvio, idunidad=unidad.idunidad))
        ShipmentUnitController._auditar(
            db, current_user, envio.idtenant, request, "ASIGNAR_UNIDAD_ENVIO", envio.idenvio
        )
        db.commit()

        asignadas = ShipmentUnitController._asignadas(db, envio.idenvio)
        return EnvioUnidadActionResponse(
            message=f"Unidad {unidad.numeroserie} asignada al envio {envio.codigoenvio}.",
            unidades=asignadas
        )

    @staticmethod
    def assign_units_bulk(
        db: Session,
        current_user: User,
        request: Request,
        idenvio: int,
        body: EnvioUnidadBulkAssignRequest
    ) -> EnvioUnidadActionResponse:
        envio = ShipmentUnitController._get_envio_or_404(db, current_user, idenvio)
        ShipmentUnitController._validar_envio_asignable(envio)

        # Toda la operacion es atomica: si una unidad falla, no se asigna ninguna.
        preparado = []
        for idunidad in body.unidades:
            preparado.append(ShipmentUnitController._preparar_asignacion(db, envio, envio.idtenant, idunidad))

        for unidad in preparado:
            db.add(EnvioUnidad(idenvio=envio.idenvio, idunidad=unidad.idunidad))

        ShipmentUnitController._auditar(
            db, current_user, envio.idtenant, request, "ASIGNAR_UNIDADES_ENVIO", envio.idenvio
        )
        db.commit()

        series = ", ".join(u.numeroserie for u in preparado)
        return EnvioUnidadActionResponse(
            message=f"{len(preparado)} unidad(es) asignadas al envio {envio.codigoenvio}: {series}.",
            unidades=ShipmentUnitController._asignadas(db, envio.idenvio)
        )

    @staticmethod
    def unassign_unit(
        db: Session,
        current_user: User,
        request: Request,
        idenvio: int,
        idunidad: int
    ) -> EnvioUnidadActionResponse:
        envio = ShipmentUnitController._get_envio_or_404(db, current_user, idenvio)
        ShipmentUnitController._validar_envio_asignable(envio)

        vinculo = db.execute(
            select(EnvioUnidad).where(
                EnvioUnidad.idenvio == envio.idenvio,
                EnvioUnidad.idunidad == idunidad
            )
        ).scalar_one_or_none()

        if not vinculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La unidad {idunidad} no esta asignada al envio {envio.codigoenvio}."
            )

        unidad = db.execute(
            select(UnidadProducto).where(UnidadProducto.idunidad == idunidad)
        ).scalar_one_or_none()

        db.delete(vinculo)
        db.flush()

        ShipmentUnitController._auditar(
            db, current_user, envio.idtenant, request, "DESASIGNAR_UNIDAD_ENVIO", envio.idenvio
        )
        db.commit()

        return EnvioUnidadActionResponse(
            message=(
                f"Unidad {unidad.numeroserie if unidad else idunidad} desasignada "
                f"del envio {envio.codigoenvio}."
            ),
            unidades=ShipmentUnitController._asignadas(db, envio.idenvio)
        )


# Rutas FastAPI
@router.get("/{idenvio}/units", response_model=EnvioUnidadesResponse)
def list_unidades_route(
    idenvio: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar las unidades asignadas al envio y las candidatas disponibles (CU-020)."""
    return ShipmentUnitController.list_unidades(db, current_user, idenvio)


@router.post("/{idenvio}/units", response_model=EnvioUnidadActionResponse)
def assign_unidad_route(
    idenvio: int,
    body: EnvioUnidadAssignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_shipment_management)
):
    """Asignar una unidad fisica al envio (CU-020)."""
    return ShipmentUnitController.assign_unit(db, current_user, request, idenvio, body)


@router.post("/{idenvio}/units/bulk", response_model=EnvioUnidadActionResponse)
def assign_unidades_bulk_route(
    idenvio: int,
    body: EnvioUnidadBulkAssignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_shipment_management)
):
    """Asignar varias unidades fisicas al envio en una sola operacion (CU-020)."""
    return ShipmentUnitController.assign_units_bulk(db, current_user, request, idenvio, body)


@router.delete("/{idenvio}/units/{idunidad}", response_model=EnvioUnidadActionResponse)
def unassign_unidad_route(
    idenvio: int,
    idunidad: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_shipment_management)
):
    """Desasignar una unidad fisica del envio (CU-020)."""
    return ShipmentUnitController.unassign_unit(db, current_user, request, idenvio, idunidad)
