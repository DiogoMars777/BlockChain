from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, String

from app.db.session import get_db
from app.models.cu012_recepciones.reception import RecepcionCompra, RecepcionDetalle
from app.models.cu010_ordenes_compra.purchase import Compra, CompraDetalle
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu020_asignacion_unidades_envio.shipment_unit import EnvioUnidad
from app.models.cu005_bitacora.bitacora import Bitacora
from app.models.cu005_bitacora.notification import Notificacion
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.controllers.shared import get_bolivia_now, get_client_ip, require_roles
from app.views.cu012_recepciones.reception_views import (
    RecepcionResponse,
    RecepcionFullResponse,
    RecepcionCreate,
    RecepcionEstadoUpdate,
    RecepcionActionResponse,
    RecepcionDetalleResponse
)

router = APIRouter(prefix="/receptions", tags=["Gestionar Recepciones de Mercancia (CU-012)"])

# Roles autorizados a registrar recepciones de mercancia.
ROLES_GESTION_RECEPCION = ("SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones")

requires_recepcion_management = require_roles(*ROLES_GESTION_RECEPCION)

# Transiciones validas del ciclo de vida de una recepcion.
# 'completa' y 'rechazada' son estados finales.
TRANSICIONES_RECEPCION = {
    "pendiente": {"parcial", "completa", "rechazada"},
    "parcial": {"parcial", "completa", "rechazada"},
    "completa": set(),
    "rechazada": set(),
}

ESTADOS_RECEPCION = set(TRANSICIONES_RECEPCION.keys())


class ReceptionController:

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
    def _get_recepcion_or_404(db: Session, current_user: User, idrecepcion: int) -> RecepcionCompra:
        tenant_id = ReceptionController._tenant_id(current_user)
        recepcion = db.execute(
            select(RecepcionCompra)
            .join(Compra, RecepcionCompra.idcompra == Compra.idcompra)
            .where(
                RecepcionCompra.idrecepcion == idrecepcion,
                Compra.idtenant == tenant_id
            )
        ).scalar_one_or_none()
        if not recepcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recepcion con ID {idrecepcion} no encontrada o no pertenece a la empresa."
            )
        return recepcion

    @staticmethod
    def _get_idusuariotenant(db: Session, current_user: User, tenant_id: int):
        stmt_ut = select(UsuarioTenant.idusuariotenant).where(
            UsuarioTenant.idusuario == current_user.idusuario,
            UsuarioTenant.idtenant == tenant_id
        )
        idut = db.execute(stmt_ut).scalar()
        if not idut:
            stmt_ut2 = select(UsuarioTenant.idusuariotenant).where(
                UsuarioTenant.idusuario == current_user.idusuario
            )
            idut = db.execute(stmt_ut2).scalar()
        return idut

    @staticmethod
    def _serializar(
        recepcion: RecepcionCompra,
        compras: dict,
        ubicaciones: dict,
        total_recibido: int
    ) -> RecepcionResponse:
        compra = compras.get(recepcion.idcompra)
        return RecepcionResponse(
            idrecepcion=recepcion.idrecepcion,
            idtenant=compra.idtenant if compra else 0,
            idcompra=recepcion.idcompra,
            numeroorden=compra.numeroorden if compra else None,
            idproveedor=compra.idproveedor if compra else None,
            proveedor_nombre=(
                (compra.proveedor.razonsocial or compra.proveedor.nombre)
                if compra and compra.proveedor else None
            ),
            idubicacion=recepcion.idubicacion,
            ubicacion_nombre=ubicaciones.get(recepcion.idubicacion),
            fecharecepcion=recepcion.fecharecepcion,
            numerodocumento=recepcion.numerodocumento,
            estado=str(recepcion.estado),
            total_recibido=total_recibido
        )

    @staticmethod
    def _contexto_recepciones(db: Session, recepciones: List[RecepcionCompra]) -> tuple:
        """Resuelve compras, ubicaciones y totales en una sola consulta por tipo."""
        ids_compra = {r.idcompra for r in recepciones}
        ids_ubicacion = {r.idubicacion for r in recepciones}
        ids_recepcion = [r.idrecepcion for r in recepciones]

        compras = {}
        if ids_compra:
            compras = {
                c.idcompra: c
                for c in db.execute(
                    select(Compra).where(Compra.idcompra.in_(ids_compra))
                ).scalars().all()
            }

        ubicaciones = {}
        if ids_ubicacion:
            ubicaciones = {
                f.idubicacion: f.nombre
                for f in db.execute(
                    select(Ubicacion.idubicacion, Ubicacion.nombre)
                    .where(Ubicacion.idubicacion.in_(ids_ubicacion))
                ).all()
            }

        totales = {}
        if ids_recepcion:
            totales = {
                f[0]: f[1]
                for f in db.execute(
                    select(
                        RecepcionDetalle.idrecepcion,
                        func.coalesce(func.sum(RecepcionDetalle.cantidadrecibida), 0)
                    )
                    .where(RecepcionDetalle.idrecepcion.in_(ids_recepcion))
                    .group_by(RecepcionDetalle.idrecepcion)
                ).all()
            }

        return compras, ubicaciones, totales

    @staticmethod
    def _unidades_por_detalle(db: Session, ids_detalle: List[int]) -> dict:
        if not ids_detalle:
            return {}
        filas = db.execute(
            select(UnidadProducto.idrecepciondetalle, func.count(UnidadProducto.idunidad))
            .where(UnidadProducto.idrecepciondetalle.in_(ids_detalle))
            .group_by(UnidadProducto.idrecepciondetalle)
        ).all()
        return {f[0]: f[1] for f in filas}

    @staticmethod
    def _detalles(db: Session, idrecepcion: int) -> List[RecepcionDetalleResponse]:
        filas = db.execute(
            select(
                RecepcionDetalle.idrecepciondetalle,
                RecepcionDetalle.idvariante,
                RecepcionDetalle.cantidadesperada,
                RecepcionDetalle.cantidadrecibida,
                VarianteProducto.sku,
                Producto.nombre
            )
            .join(VarianteProducto, RecepcionDetalle.idvariante == VarianteProducto.idvariante)
            .join(Producto, VarianteProducto.idproducto == Producto.idproducto)
            .where(RecepcionDetalle.idrecepcion == idrecepcion)
            .order_by(RecepcionDetalle.idrecepciondetalle)
        ).all()

        generadas = ReceptionController._unidades_por_detalle(
            db, [f.idrecepciondetalle for f in filas]
        )

        return [
            RecepcionDetalleResponse(
                idrecepciondetalle=f.idrecepciondetalle,
                idvariante=f.idvariante,
                sku=f.sku,
                producto_nombre=f.nombre,
                cantidadesperada=f.cantidadesperada,
                cantidadrecibida=f.cantidadrecibida,
                unidades_generadas=generadas.get(f.idrecepciondetalle, 0)
            )
            for f in filas
        ]

    @staticmethod
    def _get_full(db: Session, current_user: User, idrecepcion: int) -> RecepcionFullResponse:
        recepcion = ReceptionController._get_recepcion_or_404(db, current_user, idrecepcion)
        compras, ubicaciones, totales = ReceptionController._contexto_recepciones(db, [recepcion])
        base = ReceptionController._serializar(
            recepcion, compras, ubicaciones, int(totales.get(recepcion.idrecepcion, 0))
        )
        return RecepcionFullResponse(
            **base.model_dump(),
            detalles=ReceptionController._detalles(db, recepcion.idrecepcion)
        )

    @staticmethod
    def list_recepciones(
        db: Session,
        current_user: User,
        estado: Optional[str] = None,
        idcompra: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[RecepcionResponse]:
        tenant_id = ReceptionController._tenant_id(current_user)

        query = (
            select(RecepcionCompra)
            .join(Compra, RecepcionCompra.idcompra == Compra.idcompra)
            .where(Compra.idtenant == tenant_id)
        )

        if estado and estado.strip():
            # estado es un enum de Postgres: hay que castear a texto para usar lower()
            query = query.where(
                func.lower(cast(RecepcionCompra.estado, String)) == estado.strip().lower()
            )

        if idcompra:
            query = query.where(RecepcionCompra.idcompra == idcompra)

        query = query.order_by(RecepcionCompra.idrecepcion.desc()).offset(skip).limit(limit)
        recepciones = list(db.execute(query).scalars().all())

        compras, ubicaciones, totales = ReceptionController._contexto_recepciones(db, recepciones)

        return [
            ReceptionController._serializar(
                r, compras, ubicaciones, int(totales.get(r.idrecepcion, 0))
            )
            for r in recepciones
        ]

    @staticmethod
    def get_recepcion(db: Session, current_user: User, idrecepcion: int) -> RecepcionFullResponse:
        return ReceptionController._get_full(db, current_user, idrecepcion)

    @staticmethod
    def _validar_detalles(db: Session, body: RecepcionCreate) -> List[tuple]:
        """Valida cada linea de detalle contra la orden de compra."""
        if not body.detalles:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La recepcion debe incluir al menos un detalle de producto."
            )

        vistos = set()
        validas = []
        for det in body.detalles:
            if det.idvariante in vistos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La variante {det.idvariante} aparece repetida en el detalle de la recepcion."
                )
            vistos.add(det.idvariante)

            if det.cantidadrecibida > det.cantidadesperada:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Para la variante {det.idvariante} la cantidad recibida "
                           f"({det.cantidadrecibida}) no puede superar la esperada ({det.cantidadesperada})."
                )

            detalle_compra = db.execute(
                select(CompraDetalle).where(
                    CompraDetalle.idcompra == body.idcompra,
                    CompraDetalle.idvariante == det.idvariante
                )
            ).scalar_one_or_none()

            if not detalle_compra:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La variante {det.idvariante} no forma parte de la orden de compra indicada."
                )

            validas.append((det.idvariante, det.cantidadesperada, det.cantidadrecibida))

        return validas

    @staticmethod
    def _sincronizar_estado_compra(db: Session, idcompra: int) -> str:
        """Recalcula el estado de la orden de compra segun lo efectivamente recibido."""
        # Sin flush explicito la consulta podria leer un estado de recepcion aun
        # no escrito (la sesion puede venir con autoflush desactivado).
        db.flush()

        compra = db.execute(
            select(Compra).where(Compra.idcompra == idcompra)
        ).scalar_one_or_none()

        if not compra:
            return ""

        if str(compra.estado).lower() == "cancelada":
            return str(compra.estado)

        detalles = db.execute(
            select(CompraDetalle.idvariante, CompraDetalle.cantidad).where(
                CompraDetalle.idcompra == idcompra
            )
        ).all()

        recibido_por_variante = {
            f[0]: f[1]
            for f in db.execute(
                select(
                    RecepcionDetalle.idvariante,
                    func.coalesce(func.sum(RecepcionDetalle.cantidadrecibida), 0)
                )
                .join(RecepcionCompra, RecepcionDetalle.idrecepcion == RecepcionCompra.idrecepcion)
                .where(
                    RecepcionCompra.idcompra == idcompra,
                    RecepcionCompra.estado != "rechazada"
                )
                .group_by(RecepcionDetalle.idvariante)
            ).all()
        }

        pendientes = sum(
            max(0, esperado - recibido_por_variante.get(idvariante, 0))
            for idvariante, esperado in detalles
        )
        recibido_total = sum(recibido_por_variante.values())

        if recibido_total == 0:
            nuevo = "enviada"
        elif pendientes == 0:
            nuevo = "recibida_total"
        else:
            nuevo = "recibida_parcial"

        compra.estado = nuevo
        return nuevo

    @staticmethod
    def create_recepcion(
        db: Session,
        current_user: User,
        request: Request,
        body: RecepcionCreate
    ) -> RecepcionActionResponse:
        tenant_id = ReceptionController._tenant_id(current_user)

        compra = db.execute(
            select(Compra).where(Compra.idcompra == body.idcompra, Compra.idtenant == tenant_id)
        ).scalar_one_or_none()

        if not compra:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden de compra con ID {body.idcompra} no encontrada o no pertenece a la empresa."
            )

        if str(compra.estado).lower() not in ("enviada", "recibida_parcial"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se puede registrar una recepcion sobre una orden 'enviada' o "
                       f"'recibida_parcial'. El estado actual es '{compra.estado}'."
            )

        ubicacion = db.execute(
            select(Ubicacion).where(
                Ubicacion.idubicacion == body.idubicacion,
                Ubicacion.idtenant == tenant_id
            )
        ).scalar_one_or_none()

        if not ubicacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La ubicacion indicada no existe o no pertenece a la empresa."
            )

        estado = (body.estado or "pendiente").strip().lower()
        if estado not in ESTADOS_RECEPCION:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado '{estado}' no valido. Permitidos: {sorted(ESTADOS_RECEPCION)}."
            )

        lineas = ReceptionController._validar_detalles(db, body)
        ahora = get_bolivia_now()

        recepcion = RecepcionCompra(
            idcompra=body.idcompra,
            idubicacion=body.idubicacion,
            fecharecepcion=ahora,
            numerodocumento=body.numerodocumento.strip(),
            estado=estado
        )
        db.add(recepcion)
        db.flush()

        unidades_generadas = 0
        prefijo = f"REC-{recepcion.numerodocumento.upper()}"

        for idvariante, esperado, recibido in lineas:
            detalle = RecepcionDetalle(
                idrecepcion=recepcion.idrecepcion,
                idvariante=idvariante,
                cantidadesperada=esperado,
                cantidadrecibida=recibido
            )
            db.add(detalle)
            db.flush()

            # Actualizacion de existencias: una unidad fisica por pieza recibida.
            # idrecepciondetalle queda fijado tras el flush, que ya asigno el id del detalle.
            if recibido > 0 and estado != "rechazada":
                unidades_generadas += recibido
                for i in range(1, recibido + 1):
                    db.add(UnidadProducto(
                        idtenant=tenant_id,
                        idvariante=idvariante,
                        idrecepciondetalle=detalle.idrecepciondetalle,
                        numeroserie=f"{prefijo}-{detalle.idrecepciondetalle}-{i:04d}",
                        idubicacionactual=body.idubicacion,
                        estado="disponible"
                    ))

        estado_compra = ReceptionController._sincronizar_estado_compra(db, body.idcompra)

        idut = ReceptionController._get_idusuariotenant(db, current_user, tenant_id)
        if idut:
            db.add(Bitacora(
                idusuariotenant=idut,
                accion="REGISTRAR_RECEPCION",
                entidad="RecepcionCompra",
                identidad=recepcion.idrecepcion,
                ip=get_client_ip(request),
                fechahora=ahora
            ))
            db.add(Notificacion(
                idusuariotenant=idut,
                titulo=f"Recepcion {recepcion.numerodocumento} registrada",
                contenido=(
                    f"Se recibieron {unidades_generadas} unidad(es) de la orden de compra "
                    f"#{compra.numeroorden} en {ubicacion.nombre}. "
                    f"Estado de la orden: {estado_compra}."
                ),
                leida=False,
                fechaenvio=ahora,
                enlaceaccion=f"/receptions/{recepcion.idrecepcion}"
            ))

        db.commit()
        db.refresh(recepcion)

        return RecepcionActionResponse(
            message=(
                f"Recepcion #{recepcion.numerodocumento} registrada. "
                f"{unidades_generadas} unidad(es) incorporadas a existencias."
            ),
            recepcion=ReceptionController._get_full(db, current_user, recepcion.idrecepcion)
        )

    @staticmethod
    def _retirar_unidades(db: Session, idrecepcion: int) -> int:
        """Da de baja las unidades aun disponibles que genero una recepcion rechazada."""
        ids_detalle = db.execute(
            select(RecepcionDetalle.idrecepciondetalle).where(
                RecepcionDetalle.idrecepcion == idrecepcion
            )
        ).scalars().all()

        if not ids_detalle:
            return 0

        # No se desvinculan unidades ya despachadas en un envio logistico.
        en_envio = set(
            db.execute(
                select(EnvioUnidad.idunidad).where(
                    EnvioUnidad.idunidad.in_(
                        select(UnidadProducto.idunidad).where(
                            UnidadProducto.idrecepciondetalle.in_(ids_detalle)
                        )
                    )
                )
            ).scalars().all()
        )

        retiradas = 0
        for unidad in db.execute(
            select(UnidadProducto).where(UnidadProducto.idrecepciondetalle.in_(ids_detalle))
        ).scalars().all():
            if str(unidad.estado).lower() == "disponible" and unidad.idunidad not in en_envio:
                db.delete(unidad)
                retiradas += 1

        return retiradas

    @staticmethod
    def update_estado(
        db: Session,
        current_user: User,
        request: Request,
        idrecepcion: int,
        body: RecepcionEstadoUpdate
    ) -> RecepcionActionResponse:
        recepcion = ReceptionController._get_recepcion_or_404(db, current_user, idrecepcion)

        actual = str(recepcion.estado)
        nuevo = body.estado.strip().lower()

        if nuevo not in ESTADOS_RECEPCION:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado '{nuevo}' no valido. Permitidos: {sorted(ESTADOS_RECEPCION)}."
            )

        if nuevo == actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La recepcion ya se encuentra en estado '{nuevo}'."
            )

        permitidos = TRANSICIONES_RECEPCION[actual]
        if nuevo not in permitidos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se permite pasar de '{actual}' a '{nuevo}'. "
                       f"Desde '{actual}' solo se puede ir a: {sorted(permitidos) or ['estado final']}."
            )

        ahora = get_bolivia_now()
        recepcion.estado = nuevo
        db.flush()

        retiradas = ReceptionController._retirar_unidades(db, recepcion.idrecepcion) if nuevo == "rechazada" else 0
        estado_compra = ReceptionController._sincronizar_estado_compra(db, recepcion.idcompra)

        tenant_id = ReceptionController._tenant_id(current_user)
        idut = ReceptionController._get_idusuariotenant(db, current_user, tenant_id)
        if idut:
            db.add(Bitacora(
                idusuariotenant=idut,
                accion="CAMBIAR_ESTADO_RECEPCION",
                entidad="RecepcionCompra",
                identidad=recepcion.idrecepcion,
                ip=get_client_ip(request),
                fechahora=ahora
            ))

        db.commit()
        db.refresh(recepcion)

        extra = f" {retiradas} unidad(es) retiradas de existencias." if retiradas else ""
        return RecepcionActionResponse(
            message=(
                f"Recepcion #{recepcion.numerodocumento} actualizada a '{nuevo}'. "
                f"Estado de la orden de compra: {estado_compra or 'sin cambios'}.{extra}"
            ),
            recepcion=ReceptionController._get_full(db, current_user, recepcion.idrecepcion)
        )


# Rutas FastAPI
@router.get("", response_model=List[RecepcionResponse])
def list_recepciones_route(
    estado: Optional[str] = Query(None, description="Filtrar por estado de la recepcion (pendiente, parcial, completa, rechazada)"),
    idcompra: Optional[int] = Query(None, description="Filtrar recepciones de una orden de compra"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar recepciones de mercancia del tenant (CU-012)."""
    return ReceptionController.list_recepciones(db, current_user, estado, idcompra, skip, limit)


@router.get("/{idrecepcion}", response_model=RecepcionFullResponse)
def get_recepcion_route(
    idrecepcion: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener el detalle de una recepcion con sus productos recibidos (CU-012)."""
    return ReceptionController.get_recepcion(db, current_user, idrecepcion)


@router.post("", response_model=RecepcionActionResponse, status_code=status.HTTP_201_CREATED)
def create_recepcion_route(
    body: RecepcionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_recepcion_management)
):
    """Registrar la recepcion de mercancia y actualizar existencias (CU-012)."""
    return ReceptionController.create_recepcion(db, current_user, request, body)


@router.patch("/{idrecepcion}/estado", response_model=RecepcionActionResponse)
def update_recepcion_estado_route(
    idrecepcion: int,
    body: RecepcionEstadoUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_recepcion_management)
):
    """Actualizar el estado de una recepcion (CU-012)."""
    return ReceptionController.update_estado(db, current_user, request, idrecepcion, body)
