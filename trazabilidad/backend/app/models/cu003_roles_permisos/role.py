from typing import Optional, List
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(Base):
    __tablename__ = "rol"

    idrol: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombrerol: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    role_permissions = relationship("RolPermiso", back_populates="role", cascade="all, delete-orphan")
    usuario_tenant_roles = relationship("UsuarioTenantRol", back_populates="role", cascade="all, delete-orphan")
