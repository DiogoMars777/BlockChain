from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class EnvioUnidadResponse(BaseModel):
    idenviounidad: int
    idunidad: int
    numeroserie: str
    idvariante: Optional[int] = None
    sku: Optional[str] = None
    producto_nombre: Optional[str] = None
    estado: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EnvioResponse(BaseModel):
    idenvio: int
    idtenant: int
    codigoenvio: str
    idactororigen: int
    idactordestino: int
    idtransportista: Optional[int] = None
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


class EnvioDetalleResponse(EnvioResponse):
    """Detalle de un envío, con las unidades asignadas (CU-019 / CU-020)."""

    unidades: List[EnvioUnidadResponse] = []

    model_config = ConfigDict(from_attributes=True)


class EnvioCreate(BaseModel):
    idactororigen: int = Field(..., description="Actor de la cadena que origina el envío")
    idactordestino: int = Field(..., description="Actor de la cadena que recibe el envío")
    idtransportista: Optional[int] = Field(None, description="Transportista internacional, opcional")
    codigoenvio: str = Field(..., min_length=1, max_length=50, description="Código de envío, único en el sistema")
    fechaestimada: Optional[datetime] = None
    trackingexterno: Optional[str] = Field(None, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class EnvioUpdate(BaseModel):
    idactordestino: Optional[int] = None
    idtransportista: Optional[int] = None
    fechaestimada: Optional[datetime] = None
    trackingexterno: Optional[str] = Field(None, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class EnvioEstadoUpdate(BaseModel):
    estado: str = Field(..., description="Nuevo estado: preparacion, en_transito, entregado, retrasado o cancelado")

    model_config = ConfigDict(from_attributes=True)
