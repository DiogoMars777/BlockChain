from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class CondicionTransporteInput(BaseModel):
    temperatura: Optional[Decimal] = Field(None, description="Temperatura en grados Celsius (°C)")
    humedad: Optional[Decimal] = Field(None, description="Humedad relativa en porcentaje (%)")
    presion: Optional[Decimal] = Field(None, description="Presión atmosférica en hPa")
    nivelvibracion: Optional[Decimal] = Field(None, description="Nivel de aceleración o impacto en G")
    fuentedatos: Optional[str] = Field("App Móvil Conductor", description="Fuente de lectura (Sensor BLE, GPS, Manual)")


class CondicionTransporteResponse(BaseModel):
    idcondicion: int
    idevento: int
    temperatura: Optional[Decimal] = None
    humedad: Optional[Decimal] = None
    presion: Optional[Decimal] = None
    nivelvibracion: Optional[Decimal] = None
    timestampregistro: Optional[datetime] = None
    fuentedatos: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CreateTransportEventRequest(BaseModel):
    tipoevento: str = Field(..., description="Tipo de hito (transporte_maritimo, transporte_aereo, transporte_terrestre, llegada_puerto, despacho_aduanero, recepcion_almacen, etc.)")
    idubicacion: int = Field(..., description="ID de la ubicación física del evento")
    descripcion: Optional[str] = Field(None, max_length=500, description="Observaciones o bitácora de campo")
    idactordestino: Optional[int] = Field(None, description="ID del actor de destino si cambia de custodia")
    condiciones: Optional[CondicionTransporteInput] = None


class EventoTrazabilidadResponse(BaseModel):
    idevento: int
    idtenant: int
    tipoevento: str
    fechahora: datetime
    idubicacion: int
    ubicacion_nombre: Optional[str] = None
    usuario_nombre: Optional[str] = None
    descripcion: Optional[str] = None
    payloadhash: Optional[str] = None
    estadoverificacion: Optional[str] = None
    condiciones: Optional[CondicionTransporteResponse] = None

    model_config = ConfigDict(from_attributes=True)


class EnvioResponse(BaseModel):
    idenvio: int
    idtenant: int
    codigoenvio: str
    actor_origen_nombre: Optional[str] = None
    actor_destino_nombre: Optional[str] = None
    transportista_nombre: Optional[str] = None
    fechasalida: Optional[datetime] = None
    fechaestimada: Optional[datetime] = None
    fechaentrega: Optional[datetime] = None
    estado: str
    trackingexterno: Optional[str] = None
    total_unidades: int = 0

    model_config = ConfigDict(from_attributes=True)


class EnvioTimelineResponse(BaseModel):
    envio: EnvioResponse
    eventos: List[EventoTrazabilidadResponse]
    unidades_numeros: List[str] = []
