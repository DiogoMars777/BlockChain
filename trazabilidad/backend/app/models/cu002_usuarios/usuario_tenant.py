from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UsuarioTenant(Base):
    __tablename__ = "usuariotenant"

    idusuariotenant: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idusuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.idusuario", ondelete="CASCADE"), nullable=False
    )
    idtenant: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenant.idtenant", ondelete="CASCADE"), nullable=False
    )
    fechaasignacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=True
    )

    usuario = relationship("User", back_populates="usuario_tenants")
    tenant = relationship("Tenant", back_populates="usuario_tenants")
