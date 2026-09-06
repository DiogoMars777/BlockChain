from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CatalogoTenant(Base):
    __tablename__ = "catalogotenant"

    idcatalogotenant: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), nullable=False)
    idvariante: Mapped[int] = mapped_column(Integer, ForeignKey("varianteproducto.idvariante"), nullable=False)
    skuinterno: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    precioventa: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    costopromedio: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True, default=0.00)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant = relationship("Tenant")
    variante = relationship("VarianteProducto")
