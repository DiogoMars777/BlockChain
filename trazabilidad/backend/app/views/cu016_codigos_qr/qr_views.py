from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class UnitQrInfoResponse(BaseModel):
    idunidad: int
    numeroserie: str
    imei1: Optional[str] = None
    imei2: Optional[str] = None
    uuidpublico: str
    estado: str
    producto_nombre: str
    variante_sku: str
    color: Optional[str] = None
    almacenamiento: Optional[str] = None
    tiene_qr: bool
    idcodigoqr: Optional[int] = None
    tokenpublico: Optional[str] = None
    url: Optional[str] = None
    fechageneracion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GenerateQRResponse(BaseModel):
    idcodigoqr: int
    idunidad: int
    numeroserie: str
    uuidpublico: str
    tokenpublico: str
    url: str
    fechageneracion: datetime
    qr_image_url: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class BulkQRRequest(BaseModel):
    idunidades: List[int] = Field(..., min_length=1, description="Lista de IDs de unidades para generar códigos QR en lote")


class BulkQRResponse(BaseModel):
    total_generados: int
    items: List[GenerateQRResponse]
