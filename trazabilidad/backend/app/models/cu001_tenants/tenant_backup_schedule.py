from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def get_bolivia_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)


class TenantBackupSchedule(Base):
    __tablename__ = "tenant_backup_schedule"

    idschedule: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenant.idtenant", ondelete="CASCADE"), nullable=False
    )
    idusuario_creador: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.idusuario", ondelete="CASCADE"), nullable=False
    )
    fecha_hora_programada: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    frecuencia: Mapped[str] = mapped_column(
        String(20), default="UNA_VEZ", nullable=False
    )  # "UNA_VEZ", "DIARIO", "SEMANAL", "MENSUAL"
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default="PROGRAMADO", nullable=False
    )  # "PROGRAMADO", "EJECUTADO", "CANCELADO", "FALLIDO"
    ultimo_ejecutado: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    proxima_ejecucion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    mensaje_resultado: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fechacreacion: Mapped[datetime] = mapped_column(
        DateTime, default=get_bolivia_now, nullable=False
    )

    tenant = relationship("Tenant", foreign_keys=[idtenant])
    usuario_creador = relationship("User", foreign_keys=[idusuario_creador])
