from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

ESTADO_RECEPCION_ENUM = Enum(
    'pendiente',
    'parcial',
    'completa',
    'rechazada',
    name='estado_recepcion_enum',
    create_type=False
)


class RecepcionCompra(Base):
    """Recepción física de la mercancía en Bolivia (CU-012)."""

    __tablename__ = "recepcioncompra"

    idrecepcion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idcompra: Mapped[int] = mapped_column(Integer, ForeignKey("compra.idcompra"), nullable=False)
    idubicacion: Mapped[int] = mapped_column(Integer, ForeignKey("ubicacion.idubicacion"), nullable=False)
    fecharecepcion: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    numerodocumento: Mapped[str] = mapped_column(String(50), nullable=False)
    estado: Mapped[Optional[str]] = mapped_column(ESTADO_RECEPCION_ENUM, nullable=True, default="pendiente")

    compra = relationship("Compra", back_populates="recepciones")
    ubicacion = relationship("Ubicacion")
    detalles = relationship("RecepcionDetalle", back_populates="recepcion", cascade="all, delete-orphan")


class RecepcionDetalle(Base):
    """Detalle de productos recibidos (CU-012)."""

    __tablename__ = "recepciondetalle"

    idrecepciondetalle: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idrecepcion: Mapped[int] = mapped_column(Integer, ForeignKey("recepcioncompra.idrecepcion"), nullable=False)
    idvariante: Mapped[int] = mapped_column(Integer, ForeignKey("varianteproducto.idvariante"), nullable=False)
    cantidadesperada: Mapped[int] = mapped_column(Integer, nullable=False)
    cantidadrecibida: Mapped[int] = mapped_column(Integer, nullable=False)

    recepcion = relationship("RecepcionCompra", back_populates="detalles")
    variante = relationship("VarianteProducto")
