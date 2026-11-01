from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

TIPO_ANOMALIA_ENUM = Enum(
    'fraude_autenticidad',
    'empaque_vulnerado',
    'discrepancia_serial',
    name='tipo_anomalia_enum',
    create_type=False
)

ESTADO_REPORTE_ENUM = Enum(
    'pendiente',
    'en_revision',
    'resuelta',
    'rechazada',
    name='estado_reporte_enum',
    create_type=False
)

GRAVEDAD_REPORTE_ENUM = Enum(
    'baja',
    'media',
    'alta',
    'critica',
    name='gravedad_reporte_enum',
    create_type=False
)


class ReporteSospecha(Base):
    __tablename__ = "reportesospecha"

    idreporte: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigoticket: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), index=True, nullable=False)
    idunidad: Mapped[int] = mapped_column(Integer, ForeignKey("unidadproducto.idunidad"), index=True, nullable=False)
    idusuario: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("usuario.idusuario"), nullable=True)
    tipoanomalia: Mapped[str] = mapped_column(TIPO_ANOMALIA_ENUM, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    latitud: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6), nullable=True)
    longitud: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6), nullable=True)
    estado: Mapped[str] = mapped_column(ESTADO_REPORTE_ENUM, default="pendiente", index=True, nullable=False)
    gravedad: Mapped[str] = mapped_column(GRAVEDAD_REPORTE_ENUM, default="alta", nullable=False)
    observacionresolucion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    idalerta: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("alerta.idalerta"), nullable=True)
    score_ml: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    sugerencia_ml: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    creadoen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    actualizadoen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant")
    unidad = relationship("UnidadProducto")
    usuario = relationship("User")
    alerta = relationship("Alerta")
    evidencias: Mapped[List["ReporteSospechaEvidencia"]] = relationship(
        "ReporteSospechaEvidencia", back_populates="reporte", cascade="all, delete-orphan"
    )


class ReporteSospechaEvidencia(Base):
    __tablename__ = "reportesospechaevidencia"

    idevidencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idreporte: Mapped[int] = mapped_column(Integer, ForeignKey("reportesospecha.idreporte"), index=True, nullable=False)
    nombrearchivo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipomime: Mapped[str] = mapped_column(String(100), nullable=False)
    tamanobytes: Mapped[int] = mapped_column(Integer, nullable=False)
    urlalmacenamiento: Mapped[str] = mapped_column(String(500), nullable=False)
    hashsha256: Mapped[str] = mapped_column(String(64), nullable=False)
    creadoen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    reporte: Mapped["ReporteSospecha"] = relationship("ReporteSospecha", back_populates="evidencias")

