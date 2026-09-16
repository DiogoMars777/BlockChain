from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, DateTime, Text, ForeignKey, Enum
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

TIPO_EVENTO_ENUM = Enum(
    'fabricacion',
    'control_calidad_apple',
    'exportacion',
    'transporte_maritimo',
    'transporte_aereo',
    'llegada_puerto',
    'despacho_aduanero',
    'transporte_terrestre',
    'recepcion_almacen',
    'venta',
    'devolucion',
    'retiro',
    name='tipo_evento_enum',
    create_type=False
)

ESTADO_VERIFICACION_ENUM = Enum(
    'pendiente',
    'verificado',
    'fallido',
    name='estado_verificacion_enum',
    create_type=False
)

TIPO_ALERTA_ENUM = Enum(
    'temperatura',
    'humedad',
    'vibracion',
    'retraso_aduanero',
    'vencimiento_garantia',
    'fraude_autenticidad',
    'inconsistencia_cadena',
    name='tipo_alerta_enum',
    create_type=False
)

GRAVEDAD_ALERTA_ENUM = Enum(
    'baja',
    'media',
    'alta',
    'critica',
    name='gravedad_alerta_enum',
    create_type=False
)

ESTADO_ALERTA_ENUM = Enum(
    'pendiente',
    'en_proceso',
    'resuelta',
    name='estado_alerta_enum',
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


class EnvioUnidad(Base):
    __tablename__ = "enviounidad"

    idenviounidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idenvio: Mapped[int] = mapped_column(Integer, ForeignKey("envio.idenvio"), nullable=False)
    idunidad: Mapped[int] = mapped_column(Integer, ForeignKey("unidadproducto.idunidad"), nullable=False)

    envio = relationship("Envio", back_populates="envio_unidades")
    unidad = relationship("UnidadProducto")


class EventoTrazabilidad(Base):
    __tablename__ = "eventotrazabilidad"

    idevento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), nullable=False)
    tipoevento: Mapped[str] = mapped_column(TIPO_EVENTO_ENUM, nullable=False)
    fechahora: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    idactororigen: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("actorcadena.idactor"), nullable=True)
    idactordestino: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("actorcadena.idactor"), nullable=True)
    idubicacion: Mapped[int] = mapped_column(Integer, ForeignKey("ubicacion.idubicacion"), nullable=False)
    idusuarioresponsable: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.idusuario"), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payloadhash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    estadoverificacion: Mapped[Optional[str]] = mapped_column(ESTADO_VERIFICACION_ENUM, default="pendiente")

    tenant = relationship("Tenant")
    ubicacion = relationship("Ubicacion")
    usuario_responsable = relationship("User")
    condiciones = relationship("CondicionTransporte", back_populates="evento", cascade="all, delete-orphan")
    evento_unidades = relationship("EventoUnidad", back_populates="evento", cascade="all, delete-orphan")


class EventoUnidad(Base):
    __tablename__ = "eventounidad"

    ideventounidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idevento: Mapped[int] = mapped_column(Integer, ForeignKey("eventotrazabilidad.idevento"), nullable=False)
    idunidad: Mapped[int] = mapped_column(Integer, ForeignKey("unidadproducto.idunidad"), nullable=False)

    evento = relationship("EventoTrazabilidad", back_populates="evento_unidades")
    unidad = relationship("UnidadProducto")


class CondicionTransporte(Base):
    __tablename__ = "condiciontransporte"

    idcondicion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idevento: Mapped[int] = mapped_column(Integer, ForeignKey("eventotrazabilidad.idevento"), nullable=False)
    temperatura: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    humedad: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    presion: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    nivelvibracion: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    timestampregistro: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    fuentedatos: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    evento = relationship("EventoTrazabilidad", back_populates="condiciones")


class Alerta(Base):
    __tablename__ = "alerta"

    idalerta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idtenant: Mapped[int] = mapped_column(Integer, ForeignKey("tenant.idtenant"), nullable=False)
    idunidad: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("unidadproducto.idunidad"), nullable=True)
    idevento: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("eventotrazabilidad.idevento"), nullable=True)
    tipoalerta: Mapped[str] = mapped_column(TIPO_ALERTA_ENUM, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    gravedad: Mapped[str] = mapped_column(GRAVEDAD_ALERTA_ENUM, default="media")
    fechadeteccion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecharesolucion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estado: Mapped[str] = mapped_column(ESTADO_ALERTA_ENUM, default="pendiente")
    idusuarioresolutor: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("usuario.idusuario"), nullable=True)
