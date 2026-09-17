from typing import Optional, List
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, String

from app.db.session import get_db
from app.models.cu011_compras.purchase import Compra, CompraDetalle
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu005_bitacora.bitacora import Bitacora
from app.models.cu005_bitacora.notification import Notificacion
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.views.cu011_compras.purchase_views import (
    CompraResponse,
    CompraListResponse,
    CompraDetalleResponse,
    RejectPurchaseRequest,
    ActionPurchaseResponse
)

router = APIRouter(prefix="/purchases", tags=["Aprobación de Compras (CU-011)"])


def _get_bolivia_now() -> datetime:
    """Retorna la fecha y hora oficial de Bolivia (BOT, UTC-4)."""
    return datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)


def _get_client_ip(request: Request) -> str:
    """Obtiene la IP real del cliente."""
    return (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "127.0.0.1")
    )


def _format_compra_response(compra: Compra, db: Session) -> CompraResponse:
    """Convierte un modelo Compra en un CompraResponse enriquecido con detalles y proveedor."""
    proveedor_nombre = None
    if compra.idproveedor:
        stmt_prov = select(ActorCadena.razonsocial).where(ActorCadena.idactor == compra.idproveedor)
        proveedor_nombre = db.execute(stmt_prov).scalar_one_or_none()

    # Cargar detalles con nombres de producto y variante
    stmt_det = (
        select(
            CompraDetalle,
            VarianteProducto.sku,
            VarianteProducto.color,
            VarianteProducto.capacidad.label("almacenamiento"),
            Producto.nombre.label("producto_nombre")
        )
        .outerjoin(VarianteProducto, CompraDetalle.idvariante == VarianteProducto.idvariante)
        .outerjoin(Producto, VarianteProducto.idproducto == Producto.idproducto)
        .where(CompraDetalle.idcompra == compra.idcompra)
    )
    detalles_rows = db.execute(stmt_det).all()

    detalles_resp = []
    for det, sku, color, almacenamiento, producto_nombre in detalles_rows:
        detalles_resp.append(
            CompraDetalleResponse(
                idcompradetalle=det.idcompradetalle,
                idcompra=det.idcompra,
                idvariante=det.idvariante,
                sku=sku or f"VAR-{det.idvariante}",
                producto_nombre=producto_nombre or "Producto",
                color=color,
                almacenamiento=almacenamiento,
                cantidad=det.cantidad,
                costounitariousd=det.costounitariousd,
                subtotalusd=det.subtotalusd
            )
        )

    return CompraResponse(
        idcompra=compra.idcompra,
        idtenant=compra.idtenant,
        idproveedor=compra.idproveedor,
        proveedor_nombre=proveedor_nombre or f"Proveedor #{compra.idproveedor}",
        numeroorden=compra.numeroorden,
        fechacompra=compra.fechacompra,
        totalusd=compra.totalusd,
        estado=str(compra.estado),
        total_items=sum(d.cantidad for d in detalles_resp),
        detalles=detalles_resp
    )


class PurchaseController:

    @staticmethod
    def list_purchases(
        db: Session,
        current_user: User,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> CompraListResponse:
        tenant_id = current_user.tenant.idtenant if current_user.tenant else 1

        query = select(Compra).where(Compra.idtenant == tenant_id)
        if estado and estado.strip():
            query = query.where(cast(Compra.estado, String) == estado.strip().lower())

        # Total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.execute(count_stmt).scalar_one()

        query = query.order_by(Compra.idcompra.desc()).offset(skip).limit(limit)
        compras = db.execute(query).scalars().all()

        items = [_format_compra_response(c, db) for c in compras]
        return CompraListResponse(total=total, items=items)

    @staticmethod
    def get_purchase(
        db: Session,
        current_user: User,
        idcompra: int
    ) -> CompraResponse:
        tenant_id = current_user.tenant.idtenant if current_user.tenant else 1
        stmt = select(Compra).where(Compra.idcompra == idcompra, Compra.idtenant == tenant_id)
        compra = db.execute(stmt).scalar_one_or_none()

        if not compra:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden de compra con ID {idcompra} no encontrada o no pertenece a la empresa."
            )

        return _format_compra_response(compra, db)

    @staticmethod
    def approve_purchase(
        db: Session,
        current_user: User,
        request: Request,
        idcompra: int
    ) -> ActionPurchaseResponse:
        tenant_id = current_user.tenant.idtenant if current_user.tenant else 1
        stmt = select(Compra).where(Compra.idcompra == idcompra, Compra.idtenant == tenant_id)
        compra = db.execute(stmt).scalar_one_or_none()

        if not compra:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden de compra con ID {idcompra} no encontrada."
            )

        if str(compra.estado).lower() != "pendiente":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se pueden aprobar compras en estado 'pendiente'. El estado actual es '{compra.estado}'."
            )

        # Transición a enviada (orden aprobada y remitida al proveedor)
        compra.estado = "enviada"

        client_ip = _get_client_ip(request)
        hora_bolivia = _get_bolivia_now()

        # Auditoría en bitacora
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

        if idut:
            db.add(Bitacora(
                idusuariotenant=idut,
                accion="APROBAR_COMPRA",
                entidad="Compra",
                identidad=compra.idcompra,
                ip=client_ip,
                fechahora=hora_bolivia
            ))

            # Notificación de éxito
            db.add(Notificacion(
                idusuariotenant=idut,
                titulo=f"Compra #{compra.numeroorden} Aprobada",
                contenido=f"La orden de compra #{compra.numeroorden} por un total de ${compra.totalusd} USD ha sido aprobada exitosamente y enviada al proveedor.",
                leida=False,
                fechaenvio=hora_bolivia,
                enlaceaccion=f"/purchases/{compra.idcompra}"
            ))

        db.commit()
        db.refresh(compra)

        return ActionPurchaseResponse(
            message=f"Orden de compra #{compra.numeroorden} aprobada exitosamente.",
            compra=_format_compra_response(compra, db)
        )

    @staticmethod
    def reject_purchase(
        db: Session,
        current_user: User,
        request: Request,
        idcompra: int,
        body: RejectPurchaseRequest
    ) -> ActionPurchaseResponse:
        tenant_id = current_user.tenant.idtenant if current_user.tenant else 1
        stmt = select(Compra).where(Compra.idcompra == idcompra, Compra.idtenant == tenant_id)
        compra = db.execute(stmt).scalar_one_or_none()

        if not compra:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden de compra con ID {idcompra} no encontrada."
            )

        if str(compra.estado).lower() != "pendiente":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se pueden rechazar compras en estado 'pendiente'. El estado actual es '{compra.estado}'."
            )

        # Transición a cancelada
        compra.estado = "cancelada"

        client_ip = _get_client_ip(request)
        hora_bolivia = _get_bolivia_now()

        # Auditoría en bitacora
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

        if idut:
            db.add(Bitacora(
                idusuariotenant=idut,
                accion="RECHAZAR_COMPRA",
                entidad="Compra",
                identidad=compra.idcompra,
                ip=client_ip,
                fechahora=hora_bolivia
            ))

            # Notificación con el motivo
            db.add(Notificacion(
                idusuariotenant=idut,
                titulo=f"Compra #{compra.numeroorden} Rechazada",
                contenido=f"La orden de compra #{compra.numeroorden} fue rechazada. Motivo: {body.motivo}",
                leida=False,
                fechaenvio=hora_bolivia,
                enlaceaccion=f"/purchases/{compra.idcompra}"
            ))

        db.commit()
        db.refresh(compra)

        return ActionPurchaseResponse(
            message=f"Orden de compra #{compra.numeroorden} ha sido rechazada.",
            compra=_format_compra_response(compra, db)
        )


# Rutas FastAPI
@router.get("", response_model=CompraListResponse)
def list_purchases_route(
    estado: Optional[str] = Query(None, description="Filtrar por estado (pendiente, enviada, recibida_total, cancelada)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar órdenes de compra de la empresa autenticada (CU-011)."""
    return PurchaseController.list_purchases(db, current_user, estado, skip, limit)


@router.get("/{idcompra}", response_model=CompraResponse)
def get_purchase_route(
    idcompra: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener detalle completo de una orden de compra (CU-011)."""
    return PurchaseController.get_purchase(db, current_user, idcompra)


@router.patch("/{idcompra}/approve", response_model=ActionPurchaseResponse)
def approve_purchase_route(
    idcompra: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aprobar orden de compra en estado pendiente (CU-011)."""
    return PurchaseController.approve_purchase(db, current_user, request, idcompra)


@router.patch("/{idcompra}/reject", response_model=ActionPurchaseResponse)
def reject_purchase_route(
    idcompra: int,
    body: RejectPurchaseRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rechazar orden de compra en estado pendiente con motivo justificado (CU-011)."""
    return PurchaseController.reject_purchase(db, current_user, request, idcompra, body)
