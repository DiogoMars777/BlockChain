from datetime import datetime, timezone, timedelta
from typing import Set

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, UsuarioTenant, Role, UsuarioTenantRol
from app.controllers.cu004_autenticacion.auth_controller import get_current_user


def get_bolivia_now() -> datetime:
    """Retorna la fecha y hora oficial de Bolivia (BOT, UTC-4)."""
    return datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)


def get_client_ip(request: Request) -> str:
    """Obtiene la IP real del cliente, respetando el proxy inverso."""
    return (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "127.0.0.1")
    )


def get_user_tenant_id(db: Session, user: User) -> int:
    stmt = select(UsuarioTenant).where(UsuarioTenant.idusuario == user.idusuario)
    ut = db.execute(stmt).scalars().first()
    if not ut:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene un tenant asignado."
        )
    return ut.idtenant


def get_idusuariotenant(db: Session, user: User) -> int:
    """Resuelve el vinculo UsuarioTenant del usuario, priorizando la empresa activa del token."""
    tenant = getattr(user, "tenant", None)
    stmt = select(UsuarioTenant.idusuariotenant).where(
        UsuarioTenant.idusuario == user.idusuario
    )
    tenant_id = getattr(tenant, "idtenant", None)
    if tenant_id is not None:
        scoped = stmt.where(UsuarioTenant.idtenant == tenant_id)
        idut = db.execute(scoped).scalar()
        if idut:
            return idut
    idut = db.execute(stmt).scalar()
    if not idut:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una empresa asignada."
        )
    return idut


def get_user_role_names(db: Session, idusuariotenant: int) -> Set[str]:
    """Devuelve los nombres de rol del usuario dentro de una empresa."""
    stmt = (
        select(Role.nombrerol)
        .join(UsuarioTenantRol, UsuarioTenantRol.idrol == Role.idrol)
        .where(UsuarioTenantRol.idusuariotenant == idusuariotenant)
    )
    return {nombre for nombre in db.execute(stmt).scalars().all() if nombre}


def require_roles(*allowed: str):
    """Dependencia de FastAPI que exige al menos uno de los roles indicados.

    Uso:
        requiere_admin = require_roles("SuperAdministrador")

        @router.post("/algo", dependencies=[Depends(requiere_admin)])
    """
    permitidos = set(allowed)
    etiqueta = ", ".join(sorted(permitidos))

    def _dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> User:
        user_roles = getattr(current_user, "roles", []) or []
        if "SuperAdministrador" in user_roles:
            return current_user

        idut = get_idusuariotenant(db, current_user)
        roles = get_user_role_names(db, idut)
        if not (roles & permitidos or "SuperAdministrador" in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para esta operacion. Se requiere uno de estos roles: {etiqueta}."
            )
        return current_user

    return _dependency
