from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


# Notificaciones del sistema para usuarios de cada empresa (CU-005)
class Notificacion(Base):
    __tablename__ = "notificacion"

    idnotificacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idusuariotenant: Mapped[int] = mapped_column(Integer, ForeignKey("usuariotenant.idusuariotenant"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(100), nullable=False)
    contenido: Mapped[Text] = mapped_column(Text, nullable=False)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    fechaenvio: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fechalectura: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    enlaceaccion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
