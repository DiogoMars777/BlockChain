from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Producto(Base):
    __tablename__ = "producto"

    idproducto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idcategoria: Mapped[int] = mapped_column(Integer, ForeignKey("categoria.idcategoria"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="")
    paisorigen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    imagenurl: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    fechacreacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    categoria = relationship("Categoria", back_populates="productos")
    variantes = relationship("VarianteProducto", back_populates="producto", cascade="all, delete-orphan")
