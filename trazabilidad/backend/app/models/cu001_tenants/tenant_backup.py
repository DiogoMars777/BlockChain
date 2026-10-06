from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def get_bolivia_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)


class TenantBackup(Base):
    __tablename__ = "tenant_backup"

    idbackup: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenant.idtenant", ondelete="CASCADE"), nullable=False
    )
    idusuario_creador: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.idusuario", ondelete="CASCADE"), nullable=False
    )
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    cloud_storage: Mapped[str] = mapped_column(String(50), default="supabase", nullable=False)  # "supabase" | "local"
    cloud_path: Mapped[str] = mapped_column(String(500), nullable=False)
    peso_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default="PENDIENTE", nullable=False)  # PENDIENTE, PROCESANDO, COMPLETADO, FALLIDO
    mensaje_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_registros: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fechacreacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_bolivia_now,
        nullable=False
    )

    tenant = relationship("Tenant", foreign_keys=[idtenant])
    usuario_creador = relationship("User", foreign_keys=[idusuario_creador])
