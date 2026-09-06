from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Bitacora(Base):
    __tablename__ = "bitacora"

    idbitacora: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idusuariotenant: Mapped[int] = mapped_column(Integer, ForeignKey("usuariotenant.idusuariotenant"), nullable=False)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)
    entidad: Mapped[str] = mapped_column(String(50), nullable=False)
    identidad: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    fechahora: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
