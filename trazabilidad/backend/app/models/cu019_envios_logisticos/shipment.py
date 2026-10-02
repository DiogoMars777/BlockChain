from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

ESTADO_ENVIO_ENUM = Enum(
    'preparacion',
    'en_transito',
    'entregado',
    'retrasado',
    'cancelado',
    name='estado_envio_enum',
    create_type=False
)


class Envio(Base):
    __tablename__ = "envio"

    idenvio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), nullable=False)
    idactororigen: Mapped[int] = mapped_column(Integer, ForeignKey("actorcadena.idactor"), nullable=False)
    idactordestino: Mapped[int] = mapped_column(Integer, ForeignKey("actorcadena.idactor"), nullable=False)
    idtransportista: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("actorcadena.idactor"), nullable=True)
    codigoenvio: Mapped[str] = mapped_column(String(50), nullable=False)
    fechasalida: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fechaestimada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fechaentrega: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(ESTADO_ENVIO_ENUM, default="preparacion")
    trackingexterno: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    tenant = relationship("Tenant")
    actor_origen = relationship("ActorCadena", foreign_keys=[idactororigen])
    actor_destino = relationship("ActorCadena", foreign_keys=[idactordestino])
    transportista = relationship("ActorCadena", foreign_keys=[idtransportista])
    envio_unidades = relationship("EnvioUnidad", back_populates="envio", cascade="all, delete-orphan")
