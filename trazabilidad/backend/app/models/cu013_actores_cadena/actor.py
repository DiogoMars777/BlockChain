from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

TIPO_ACTOR_ENUM = Enum(
    'PROVEEDOR_EEUU',
    'TRANSPORTISTA_INTERNACIONAL',
    'ADUANA',
    'IMPORTADOR',
    'DISTRIBUIDOR',
    'TIENDA',
    'CONSUMIDOR',
    name='tipo_actor_enum',
    create_type=False
)


class ActorCadena(Base):
    __tablename__ = "actorcadena"

    idactor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    razonsocial: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tipoactor: Mapped[str] = mapped_column(TIPO_ACTOR_ENUM, nullable=False)

    tenant = relationship("Tenant")
    ubicaciones = relationship("Ubicacion", back_populates="actor", cascade="all, delete-orphan")
