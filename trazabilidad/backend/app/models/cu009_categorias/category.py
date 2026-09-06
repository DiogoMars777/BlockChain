from typing import Optional, List
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Categoria(Base):
    __tablename__ = "categoria"

    idcategoria: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombrecategoria: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    productos = relationship("Producto", back_populates="categoria")
