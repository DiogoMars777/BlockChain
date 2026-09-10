from typing import Optional, List
from datetime import date
from sqlalchemy import String, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# Certificaciones técnicas y homologaciones 
class Certificacion(Base):
    __tablename__ = "certificacion"

    idcertificacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    entidademisora: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logourl: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    productos_certificados = relationship("ProductoCertificacion", back_populates="certificacion", cascade="all, delete-orphan")


# Tabla intermedia: vincula productos con certificaciones (relación N:M)
class ProductoCertificacion(Base):
    __tablename__ = "productocertificacion"

    idproductocertificacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idproducto: Mapped[int] = mapped_column(Integer, ForeignKey("producto.idproducto"), nullable=False)
    idcertificacion: Mapped[int] = mapped_column(Integer, ForeignKey("certificacion.idcertificacion"), nullable=False)
    fechaobtencion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    certificacion = relationship("Certificacion", back_populates="productos_certificados")
