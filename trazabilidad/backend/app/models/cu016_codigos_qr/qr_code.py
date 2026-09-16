from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CodigoQR(Base):
    __tablename__ = "codigoqr"

    idcodigoqr: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idunidad: Mapped[int] = mapped_column(Integer, ForeignKey("unidadproducto.idunidad"), nullable=False)
    tokenpublico: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fechageneracion: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    unidad = relationship("UnidadProducto")
