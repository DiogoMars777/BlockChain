from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class EvidenciaResponse(BaseModel):
    idevidencia: int
    nombrearchivo: str
    tipomime: str
    tamanobytes: int
    urlalmacenamiento: str
    hashsha256: str
    creadoen: datetime

    class Config:
        from_attributes = True


class ReporteSospechaResponse(BaseModel):
    idreporte: int
    codigoticket: str
    idtenant: int
    idunidad: int
    numeroserie: Optional[str] = None
    uuidpublico: Optional[str] = None
    idusuario: Optional[int] = None
    tipoanomalia: str
    descripcion: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    estado: str
    gravedad: str
    observacionresolucion: Optional[str] = None
    idalerta: Optional[int] = None
    score_ml: Optional[Decimal] = None
    sugerencia_ml: Optional[str] = None
    creadoen: datetime
    actualizadoen: datetime
    evidencias: List[EvidenciaResponse] = []
    mensaje: Optional[str] = None

    class Config:
        from_attributes = True


class ReporteSospechaListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[ReporteSospechaResponse]


class UpdateReporteEstadoRequest(BaseModel):
    estado: str = Field(..., description="Nuevo estado: pendiente, en_revision, resuelta, rechazada")
    observacion: Optional[str] = Field(None, description="Observación obligatoria para cierre o rechazo")


# Shims de compatibilidad hacia los DTOs anteriores de CU-023
class ReportarSospechaRequest(BaseModel):
    uuidpublico: Optional[str] = None
    numeroserie: Optional[str] = None
    motivo: str = Field("fraude_autenticidad", description="Motivo / tipo de anomalía")
    descripcion: Optional[str] = None
    evidencia: Optional[str] = None
    nombrereportante: Optional[str] = None
    contactoreportante: Optional[str] = None


class ReporteSospechaLegacyResponse(BaseModel):
    idalerta: int
    referencia: str
    tipoalerta: str
    estado: str
    mensaje: str
