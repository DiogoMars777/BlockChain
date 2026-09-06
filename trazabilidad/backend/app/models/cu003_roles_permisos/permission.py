from typing import Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Permiso(Base):
    __tablename__ = "permiso"

    idpermiso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombrepermiso: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    modulo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    role_permissions = relationship("RolPermiso", back_populates="permiso", cascade="all, delete-orphan")
