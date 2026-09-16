from datetime import date
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

ESTADO_COMPRA_ENUM = Enum(
    'pendiente',
    'enviada',
    'recibida_parcial',
    'recibida_total',
    'cancelada',
    name='estado_compra_enum',
    create_type=False
)


class Compra(Base):
    __tablename__ = "compra"

    idcompra: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), nullable=False)
    idproveedor: Mapped[int] = mapped_column(Integer, ForeignKey("actorcadena.idactor"), nullable=False)
    numeroorden: Mapped[str] = mapped_column(String(50), nullable=False)
    fechacompra: Mapped[date] = mapped_column(Date, nullable=False)
    totalusd: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    estado: Mapped[Optional[str]] = mapped_column(ESTADO_COMPRA_ENUM, nullable=True, default="pendiente")

    tenant = relationship("Tenant")
    proveedor = relationship("ActorCadena")
    detalles = relationship("CompraDetalle", back_populates="compra", cascade="all, delete-orphan")


class CompraDetalle(Base):
    __tablename__ = "compradetalle"

    idcompradetalle: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idcompra: Mapped[int] = mapped_column(Integer, ForeignKey("compra.idcompra"), nullable=False)
    idvariante: Mapped[int] = mapped_column(Integer, ForeignKey("varianteproducto.idvariante"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    costounitariousd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotalusd: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    compra = relationship("Compra", back_populates="detalles")
    variante = relationship("VarianteProducto")
