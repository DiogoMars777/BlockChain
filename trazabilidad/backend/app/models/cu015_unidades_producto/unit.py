import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

ESTADO_UNIDAD_ENUM = Enum(
    'disponible',
    'vendido',
    'en_transito',
    'devuelto',
    'retirado',
    name='estado_unidad_enum',
    create_type=False
)


class UnidadProducto(Base):
    __tablename__ = "unidadproducto"

    idunidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), nullable=False)
    idvariante: Mapped[int] = mapped_column(Integer, ForeignKey("varianteproducto.idvariante"), nullable=False)
    idrecepciondetalle: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=1)
    numeroserie: Mapped[str] = mapped_column(String(100), nullable=False)
    imei1: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    imei2: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    eid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uuidpublico: Mapped[str] = mapped_column(String(100), nullable=False, default=lambda: str(uuid.uuid4()))
    idcustodioactual: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("actorcadena.idactor"), nullable=True)
    idubicacionactual: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ubicacion.idubicacion"), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(ESTADO_UNIDAD_ENUM, nullable=True, default="disponible")
    fechaingreso: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fechaventa: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    tenant = relationship("Tenant")
    variante = relationship("VarianteProducto")
    custodio = relationship("ActorCadena")
    ubicacion = relationship("Ubicacion")
