from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.db.session import get_db
from app.models.cu005_bitacora.bitacora import Bitacora
from app.models.cu005_bitacora.notification import Notificacion
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu002_usuarios.user import User
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.views.cu005_bitacora.bitacora_views import (
    BitacoraResponse,
    BitacoraListResponse,
    NotificacionResponse,
    NotificacionListResponse
)

router = APIRouter(tags=["Bitácora de Auditoría y Notificaciones (CU-005)"])


class BitacoraController:
    @staticmethod
    def list_bitacora(
        db: Session,
        accion: Optional[str] = None,
        entidad: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> BitacoraListResponse:
        query = select(Bitacora)

        if accion and accion.strip():
            query = query.where(func.lower(Bitacora.accion) == accion.strip().lower())
        if entidad and entidad.strip():
            query = query.where(func.lower(Bitacora.entidad) == entidad.strip().lower())

        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.execute(count_stmt).scalar_one()

        query = query.order_by(Bitacora.fechahora.desc()).offset(skip).limit(limit)
        items = db.execute(query).scalars().all()

        return BitacoraListResponse(
            total=total,
            items=[BitacoraResponse.model_validate(b) for b in items]
        )

    @staticmethod
    def list_notifications(
        db: Session,
        current_user: User,
        only_unread: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> NotificacionListResponse:
        # Get usuariotenant link for current user
        stmt_ut = select(UsuarioTenant.idusuariotenant).where(
            UsuarioTenant.idusuario == current_user.idusuario
        )
        idut = db.execute(stmt_ut).scalar()

        query = select(Notificacion)
        if idut:
            query = query.where(Notificacion.idusuariotenant == idut)

        if only_unread:
            query = query.where(Notificacion.leida == False)

        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.execute(count_stmt).scalar_one()

        # Count unread
        unread_stmt = select(func.count()).where(
            Notificacion.leida == False
        )
        if idut:
            unread_stmt = unread_stmt.where(Notificacion.idusuariotenant == idut)
        unread_count = db.execute(unread_stmt).scalar_one()

        query = query.order_by(Notificacion.fechaenvio.desc()).offset(skip).limit(limit)
        items = db.execute(query).scalars().all()

        return NotificacionListResponse(
            total=total,
            unread_count=unread_count,
            items=[NotificacionResponse.model_validate(n) for n in items]
        )

    @staticmethod
    def mark_notification_read(
        db: Session,
        idnotificacion: int,
        current_user: User
    ) -> NotificacionResponse:
        stmt = select(Notificacion).where(Notificacion.idnotificacion == idnotificacion)
        notif = db.execute(stmt).scalar_one_or_none()

        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notificación con ID {idnotificacion} no encontrada."
            )

        notif.leida = True
        notif.fechalectura = datetime.utcnow()
        db.commit()
        db.refresh(notif)

        return NotificacionResponse.model_validate(notif)


# Compatibilidad de alias
AuditController = BitacoraController


# Endpoints
@router.get("/bitacora", response_model=BitacoraListResponse)
def get_bitacora(
    accion: Optional[str] = Query(None, description="Filtrar por tipo de acción (ej. INSERT, UPDATE, DELETE, LOGIN)"),
    entidad: Optional[str] = Query(None, description="Filtrar por entidad (ej. Venta, Usuario, EventoTrazabilidad)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consultar registros de la bitácora de auditoría (CU-005)."""
    return BitacoraController.list_bitacora(db, accion, entidad, skip, limit)


@router.get("/notifications", response_model=NotificacionListResponse)
def get_notifications(
    only_unread: bool = Query(False, description="Filtrar solo notificaciones no leídas"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consultar las notificaciones del usuario (CU-005)."""
    return BitacoraController.list_notifications(db, current_user, only_unread, skip, limit)


@router.patch("/notifications/{idnotificacion}/read", response_model=NotificacionResponse)
def mark_notification_read(
    idnotificacion: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marcar una notificación como leída (CU-005)."""
    return BitacoraController.mark_notification_read(db, idnotificacion, current_user)
