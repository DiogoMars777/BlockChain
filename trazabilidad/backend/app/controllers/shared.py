from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UsuarioTenant


def get_user_tenant_id(db: Session, user: User) -> int:
    stmt = select(UsuarioTenant).where(UsuarioTenant.idusuario == user.idusuario)
    ut = db.execute(stmt).scalars().first()
    if not ut:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene un tenant asignado."
        )
    return ut.idtenant
