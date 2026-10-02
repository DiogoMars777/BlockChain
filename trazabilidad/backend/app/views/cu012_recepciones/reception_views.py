from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class RecepcionDetalleResponse(BaseModel):
    idrecepciondetalle: int
    idvariante: int
    sku: Optional[str] = None
    producto_nombre: Optional[str] = None
    cantidadesperada: int
    cantidadrecibida: int
    unidades_generadas: int = 0

    model_config = ConfigDict(from_attributes=True)


class RecepcionResponse(BaseModel):
    idrecepcion: int
    idtenant: int
    idcompra: int
    numeroorden: Optional[str] = None
    idproveedor: Optional[int] = None
    proveedor_nombre: Optional[str] = None
    idubicacion: int
    ubicacion_nombre: Optional[str] = None
    fecharecepcion: Optional[datetime] = None
    numerodocumento: str
    estado: str
    total_recibido: int = 0

    model_config = ConfigDict(from_attributes=True)


class RecepcionDetalleInput(BaseModel):
    idvariante: int
    cantidadesperada: int = Field(..., ge=1)
    cantidadrecibida: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class RecepcionFullResponse(RecepcionResponse):
    """Recepción con el detalle de productos recibidos (CU-012)."""

    detalles: List[RecepcionDetalleResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RecepcionCreate(BaseModel):
    idcompra: int = Field(..., description="Orden de compra que se está recibiendo")
    idubicacion: int = Field(..., description="Ubicación física donde se recibe la mercancía")
    numerodocumento: str = Field(..., min_length=1, max_length=50, description="Número de remisión o documento de recepción")
    estado: str = Field("pendiente", description="pendiente, parcial, completa o rechazada")
    detalles: List[RecepcionDetalleInput] = []

    model_config = ConfigDict(from_attributes=True)


class RecepcionEstadoUpdate(BaseModel):
    estado: str = Field(..., description="Nuevo estado: pendiente, parcial, completa o rechazada")

    model_config = ConfigDict(from_attributes=True)


class RecepcionActionResponse(BaseModel):
    message: str
    recepcion: RecepcionFullResponse

    model_config = ConfigDict(from_attributes=True)
