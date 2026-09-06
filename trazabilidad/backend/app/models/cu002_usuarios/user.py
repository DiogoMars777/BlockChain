from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "usuario"

    idusuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombrecompleto: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    contrasenahash: Mapped[str] = mapped_column(String(255), nullable=False)
    fecharegistro: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)

    usuario_tenants = relationship("UsuarioTenant", back_populates="usuario", cascade="all, delete-orphan")
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="usuario", cascade="all, delete-orphan"
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="usuario", cascade="all, delete-orphan"
    )
