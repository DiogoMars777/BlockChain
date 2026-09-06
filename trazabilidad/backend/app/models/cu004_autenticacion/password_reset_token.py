from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PasswordResetToken(Base):
    __tablename__ = "tokenrecuperacion"

    idtoken: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tenant.idtenant", ondelete="CASCADE"), nullable=True
    )
    idusuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.idusuario", ondelete="CASCADE"), nullable=False
    )
    tokenhash: Mapped[str] = mapped_column(String(255), nullable=False)
    expiraen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usadoen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fechacreacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    usuario = relationship("User", back_populates="password_reset_tokens")
