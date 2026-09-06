from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.views.cu006_productos_variantes.product_views import VariantResponse
from app.views.cu013_actores_cadena.actor_views import ActorResponse
from app.views.cu014_ubicaciones.location_views import LocationResponse


class UnitCreate(BaseModel):
    idvariante: int
    idrecepciondetalle: Optional[int] = 1
    numeroserie: str
    imei1: Optional[str] = None
    imei2: Optional[str] = None
    eid: Optional[str] = None
    idcustodioactual: Optional[int] = None
    idubicacionactual: Optional[int] = None
    estado: Optional[str] = "disponible"


class UnitUpdate(BaseModel):
    numeroserie: Optional[str] = None
    imei1: Optional[str] = None
    imei2: Optional[str] = None
    eid: Optional[str] = None
    idcustodioactual: Optional[int] = None
    idubicacionactual: Optional[int] = None
    estado: Optional[str] = None


class UnitResponse(BaseModel):
    idunidad: int
    idtenant: int
    idvariante: int
    idrecepciondetalle: Optional[int] = 1
    numeroserie: str
    imei1: Optional[str] = None
    imei2: Optional[str] = None
    eid: Optional[str] = None
    uuidpublico: str
    idcustodioactual: Optional[int] = None
    idubicacionactual: Optional[int] = None
    estado: Optional[str] = "disponible"
    fechaingreso: datetime
    fechaventa: Optional[datetime] = None
    variante: Optional[VariantResponse] = None
    custodio: Optional[ActorResponse] = None
    ubicacion: Optional[LocationResponse] = None

    model_config = ConfigDict(from_attributes=True)


class UnitListResponse(BaseModel):
    total: int
    items: List[UnitResponse]
