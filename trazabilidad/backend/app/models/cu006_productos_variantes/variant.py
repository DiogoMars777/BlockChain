from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VarianteProducto(Base):
    __tablename__ = "varianteproducto"

    idvariante: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idproducto: Mapped[int] = mapped_column(Integer, ForeignKey("producto.idproducto"), nullable=False)
    capacidad: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="")
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="")
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    preciousd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)

    producto = relationship("Producto", back_populates="variantes")
