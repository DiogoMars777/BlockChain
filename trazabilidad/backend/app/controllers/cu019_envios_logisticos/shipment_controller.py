from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, String

from app.db.session import get_db
from app.models.cu019_envios_logisticos.shipment import Envio
from app.models.cu020_asignacion_unidades_envio.shipment_unit import EnvioUnidad
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu002_usuarios.user import User
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.controllers.shared import require_roles
from app.views.cu019_envios_logisticos.shipment_views import (
    EnvioResponse,
    EnvioDetalleResponse,
    EnvioUnidadResponse,
    EnvioCreate,
    EnvioUpdate,
    EnvioEstadoUpdate
)

router = APIRouter(prefix="/shipments", tags=["Gestión de Envíos Logísticos (CU-019)"])

# Roles autorizados a crear, editar y mover envíos.
ROLES_GESTION_ENVIO = ("SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones")

requires_shipment_management = require_roles(*ROLES_GESTION_ENVIO)

# Transiciones válidas del ciclo de vida de un envío.
# 'entregado' y 'cancelado' son estados finales.
TRANSICIONES_ENVIO = {
    "preparacion": {"en_transito", "cancelado"},
    "en_transito": {"entregado", "retrasado", "cancelado"},
    "retrasado": {"en_transito", "entregado", "cancelado"},
    "entregado": set(),
    "cancelado": set(),
}

ESTADOS_ENVIO = set(TRANSICIONES_ENVIO.keys())


class ShipmentController:

    @staticmethod
    def _get_envio_or_404(db: Session, current_user: User, idenvio: int) -> Envio:
        tenant_id = current_user.tenant.idtenant if current_user.tenant else 1
        envio = db.execute(
            select(Envio).where(Envio.idenvio == idenvio, Envio.idtenant == tenant_id)
        ).scalar_one_or_none()
        if not envio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Envío con ID {idenvio} no encontrado o no pertenece a la empresa."
            )
        return envio

    @staticmethod
    def _validar_actor(db: Session, tenant_id: int, idactor: int, campo: str) -> None:
        actor = db.execute(
            select(ActorCadena).where(
                ActorCadena.idactor == idactor,
                ActorCadena.idtenant == tenant_id
            )
        ).scalar_one_or_none()
        if not actor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El actor indicado en '{campo}' no existe o no pertenece a la empresa."
            )

    @staticmethod
    def _validar_codigoenvio(db: Session, codigoenvio: str, excluir_id: Optional[int] = None) -> str:
        # envio_codigoenvio_key es UNIQUE global
        limpio = codigoenvio.strip()
        stmt = select(Envio.idenvio).where(Envio.codigoenvio == limpio)
        if excluir_id is not None:
            stmt = stmt.where(Envio.idenvio != excluir_id)
        if db.execute(stmt).scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El código de envío '{limpio}' ya existe en el sistema."
            )
        return limpio

    @staticmethod
    def _serializar(db: Session, envio: Envio, nombres: dict, total_unidades: int) -> EnvioResponse:
        return EnvioResponse(
            idenvio=envio.idenvio,
            idtenant=envio.idtenant,
            codigoenvio=envio.codigoenvio,
            idactororigen=envio.idactororigen,
            idactordestino=envio.idactordestino,
            idtransportista=envio.idtransportista,
            actor_origen_nombre=nombres.get(envio.idactororigen) or f"Origen #{envio.idactororigen}",
            actor_destino_nombre=nombres.get(envio.idactordestino) or f"Destino #{envio.idactordestino}",
            transportista_nombre=(
                nombres.get(envio.idtransportista) or f"Transportista #{envio.idtransportista}"
                if envio.idtransportista else None
            ),
            fechasalida=envio.fechasalida,
            fechaestimada=envio.fechaestimada,
            fechaentrega=envio.fechaentrega,
            estado=str(envio.estado),
            trackingexterno=envio.trackingexterno,
            total_unidades=total_unidades
        )

    @staticmethod
    def _nombres_actores(db: Session, envios: List[Envio]) -> dict:
        """Resuelve los nombres de todos los actores de una vez, evitando N+1."""
        ids = set()
        for e in envios:
            ids.add(e.idactororigen)
            ids.add(e.idactordestino)
            if e.idtransportista:
                ids.add(e.idtransportista)
        if not ids:
            return {}
        filas = db.execute(
            select(ActorCadena.idactor, ActorCadena.razonsocial, ActorCadena.nombre)
            .where(ActorCadena.idactor.in_(ids))
        ).all()
        return {f.idactor: (f.razonsocial or f.nombre) for f in filas}

    @staticmethod
    def _conteo_unidades(db: Session, ids_envio: List[int]) -> dict:
        if not ids_envio:
            return {}
        filas = db.execute(
            select(EnvioUnidad.idenvio, func.count(EnvioUnidad.idenviounidad))
            .where(EnvioUnidad.idenvio.in_(ids_envio))
            .group_by(EnvioUnidad.idenvio)
        ).all()
        return {f[0]: f[1] for f in filas}

    @staticmethod
    def list_shipments(
        db: Session,
        current_user: User,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EnvioResponse]:
        tenant_id = current_user.tenant.idtenant if current_user.tenant else 1

        query = select(Envio).where(Envio.idtenant == tenant_id)
        if estado and estado.strip():
            # estado es un enum de Postgres: hay que castear a texto para usar lower()
            query = query.where(
                func.lower(cast(Envio.estado, String)) == estado.strip().lower()
            )

        query = query.order_by(Envio.idenvio.desc()).offset(skip).limit(limit)
        shipments = list(db.execute(query).scalars().all())

        nombres = ShipmentController._nombres_actores(db, shipments)
        conteos = ShipmentController._conteo_unidades(db, [s.idenvio for s in shipments])

        return [
            ShipmentController._serializar(db, s, nombres, conteos.get(s.idenvio, 0))
            for s in shipments
        ]

    @staticmethod
    def get_shipment(db: Session, current_user: User, idenvio: int) -> EnvioDetalleResponse:
        envio = ShipmentController._get_envio_or_404(db, current_user, idenvio)
        nombres = ShipmentController._nombres_actores(db, [envio])

        filas = db.execute(
            select(
                EnvioUnidad.idenviounidad,
                EnvioUnidad.idunidad,
                UnidadProducto.numeroserie,
                UnidadProducto.idvariante,
                UnidadProducto.estado,
                VarianteProducto.sku,
                Producto.nombre
            )
            .join(UnidadProducto, EnvioUnidad.idunidad == UnidadProducto.idunidad)
            .join(VarianteProducto, UnidadProducto.idvariante == VarianteProducto.idvariante)
            .join(Producto, VarianteProducto.idproducto == Producto.idproducto)
            .where(EnvioUnidad.idenvio == envio.idenvio)
            .order_by(UnidadProducto.numeroserie)
        ).all()

        unidades = [
            EnvioUnidadResponse(
                idenviounidad=f.idenviounidad,
                idunidad=f.idunidad,
                numeroserie=f.numeroserie,
                idvariante=f.idvariante,
                sku=f.sku,
                producto_nombre=f.nombre,
                estado=str(f.estado) if f.estado else None
            )
            for f in filas
        ]

        base = ShipmentController._serializar(db, envio, nombres, len(unidades))
        return EnvioDetalleResponse(**base.model_dump(), unidades=unidades)

    @staticmethod
    def create_shipment(db: Session, current_user: User, body: EnvioCreate) -> EnvioDetalleResponse:
        tenant_id = current_user.tenant.idtenant if current_user.tenant else 1

        ShipmentController._validar_actor(db, tenant_id, body.idactororigen, "idactororigen")
        ShipmentController._validar_actor(db, tenant_id, body.idactordestino, "idactordestino")
        if body.idtransportista:
            ShipmentController._validar_actor(db, tenant_id, body.idtransportista, "idtransportista")

        if body.idactororigen == body.idactordestino:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El actor de origen y el de destino no pueden ser el mismo."
            )

        codigoenvio = ShipmentController._validar_codigoenvio(db, body.codigoenvio)

        envio = Envio(
            idtenant=tenant_id,
            idactororigen=body.idactororigen,
            idactordestino=body.idactordestino,
            idtransportista=body.idtransportista,
            codigoenvio=codigoenvio,
            fechaestimada=body.fechaestimada,
            trackingexterno=body.trackingexterno,
            estado="preparacion"
        )

        db.add(envio)
        db.commit()
        db.refresh(envio)

        return ShipmentController.get_shipment(db, current_user, envio.idenvio)

    @staticmethod
    def update_shipment(db: Session, current_user: User, idenvio: int, body: EnvioUpdate) -> EnvioDetalleResponse:
        envio = ShipmentController._get_envio_or_404(db, current_user, idenvio)

        if str(envio.estado) != "preparacion":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se pueden editar envíos en estado 'preparacion'. El estado actual es '{envio.estado}'."
            )

        if body.idactordestino is not None:
            ShipmentController._validar_actor(db, envio.idtenant, body.idactordestino, "idactordestino")
            if body.idactordestino == envio.idactororigen:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El actor de destino no puede ser el mismo que el de origen."
                )
            envio.idactordestino = body.idactordestino

        # exclude_unset permite distinguir "no enviado" de "null explícito",
        # que es la unica forma de quitar un transportista previamente asignado.
        enviados = body.model_dump(exclude_unset=True)

        if "idtransportista" in enviados:
            if body.idtransportista is None:
                envio.idtransportista = None
            else:
                ShipmentController._validar_actor(db, envio.idtenant, body.idtransportista, "idtransportista")
                envio.idtransportista = body.idtransportista

        if body.fechaestimada is not None:
            envio.fechaestimada = body.fechaestimada

        if "trackingexterno" in enviados:
            envio.trackingexterno = body.trackingexterno

        db.commit()
        db.refresh(envio)

        return ShipmentController.get_shipment(db, current_user, envio.idenvio)

    @staticmethod
    def update_estado(db: Session, current_user: User, idenvio: int, body: EnvioEstadoUpdate) -> EnvioDetalleResponse:
        envio = ShipmentController._get_envio_or_404(db, current_user, idenvio)

        actual = str(envio.estado)
        nuevo = body.estado.strip().lower()

        if nuevo not in ESTADOS_ENVIO:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado '{nuevo}' no válido. Permitidos: {sorted(ESTADOS_ENVIO)}."
            )

        if nuevo == actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El envío ya se encuentra en estado '{nuevo}'."
            )

        permitidos = TRANSICIONES_ENVIO[actual]
        if nuevo not in permitidos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se permite pasar de '{actual}' a '{nuevo}'. "
                       f"Desde '{actual}' solo se puede ir a: {sorted(permitidos) or ['estado final']}."
            )

        ahora = datetime.now()

        if nuevo == "en_transito" and envio.fechasalida is None:
            envio.fechasalida = ahora

        if nuevo == "entregado":
            envio.fechasalida = envio.fechasalida or ahora
            envio.fechaentrega = ahora

        envio.estado = nuevo

        db.commit()
        db.refresh(envio)

        return ShipmentController.get_shipment(db, current_user, envio.idenvio)


# Rutas FastAPI
@router.get("", response_model=List[EnvioResponse])
def list_shipments_route(
    estado: Optional[str] = Query(None, description="Filtrar por estado del envío (preparacion, en_transito, entregado, retrasado, cancelado)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar envíos logísticos del tenant (CU-019)."""
    return ShipmentController.list_shipments(db, current_user, estado, skip, limit)


@router.get("/{idenvio}", response_model=EnvioDetalleResponse)
def get_shipment_route(
    idenvio: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener el detalle de un envío con sus unidades asignadas (CU-019)."""
    return ShipmentController.get_shipment(db, current_user, idenvio)


@router.post("", response_model=EnvioDetalleResponse, status_code=status.HTTP_201_CREATED)
def create_shipment_route(
    body: EnvioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_shipment_management)
):
    """Registrar un nuevo envío logístico (CU-019)."""
    return ShipmentController.create_shipment(db, current_user, body)


@router.put("/{idenvio}", response_model=EnvioDetalleResponse)
def update_shipment_route(
    idenvio: int,
    body: EnvioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_shipment_management)
):
    """Editar un envío que sigue en estado preparación (CU-019)."""
    return ShipmentController.update_shipment(db, current_user, idenvio, body)


@router.patch("/{idenvio}/estado", response_model=EnvioDetalleResponse)
def update_shipment_estado_route(
    idenvio: int,
    body: EnvioEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_shipment_management)
):
    """Mover un envío a su siguiente estado (CU-019)."""
    return ShipmentController.update_estado(db, current_user, idenvio, body)
