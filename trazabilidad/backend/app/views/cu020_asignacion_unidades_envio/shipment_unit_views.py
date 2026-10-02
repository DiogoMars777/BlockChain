from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EnvioUnidadCandidateResponse(BaseModel):
    idunidad: int
    numeroserie: str
    idvariante: int
    sku: Optional[str] = None
    producto_nombre: Optional[str] = None
    estado: Optional[str] = None
    idrecepciondetalle: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class EnvioUnidadAsignadaResponse(EnvioUnidadCandidateResponse):
    idenviounidad: int

    model_config = ConfigDict(from_attributes=True)


class EnvioUnidadesResponse(BaseModel):
    """Unidades asignadas al envio y candidatas que se pueden asignar (CU-020)."""

    idenvio: int
    codigoenvio: str
    estado: str
    asignadas: List[EnvioUnidadAsignadaResponse] = []
    disponibles: List[EnvioUnidadCandidateResponse] = []

    model_config = ConfigDict(from_attributes=True)


class EnvioUnidadAssignRequest(BaseModel):
    idunidad: int = Field(..., description="Unidad fisica a asignar al envio")

    model_config = ConfigDict(from_attributes=True)


class EnvioUnidadBulkAssignRequest(BaseModel):
    unidades: List[int] = Field(..., min_length=1, description="Lista de identificadores de unidad a asignar")

    model_config = ConfigDict(from_attributes=True)


class EnvioUnidadActionResponse(BaseModel):
    message: str
    unidades: List[EnvioUnidadAsignadaResponse] = []

    model_config = ConfigDict(from_attributes=True)
