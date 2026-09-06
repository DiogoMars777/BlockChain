from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

TIPO_UBICACION_ENUM = Enum(
    'origen',
    'almacen',
    'centro_distribucion',
    'punto_venta',
    'puerto',
    'aduana',
    name='tipo_ubicacion_enum',
    create_type=False
)


class Ubicacion(Base):
    __tablename__ = "ubicacion"

    idubicacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), nullable=False)
    idactor: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("actorcadena.idactor"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitud: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitud: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    ciudad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pais: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo: Mapped[str] = mapped_column(TIPO_UBICACION_ENUM, nullable=False)

    tenant = relationship("Tenant")
    actor = relationship("ActorCadena", back_populates="ubicaciones")
