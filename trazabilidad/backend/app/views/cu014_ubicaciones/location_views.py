from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.views.cu013_actores_cadena.actor_views import ActorResponse


class LocationCreate(BaseModel):
    nombre: str
    idactor: Optional[int] = None
    direccion: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    tipo: str


class LocationUpdate(BaseModel):
    nombre: Optional[str] = None
    idactor: Optional[int] = None
    direccion: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    tipo: Optional[str] = None


class LocationResponse(BaseModel):
    idubicacion: int
    idtenant: int
    idactor: Optional[int] = None
    nombre: str
    direccion: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    tipo: str
    actor: Optional[ActorResponse] = None

    model_config = ConfigDict(from_attributes=True)


class LocationListResponse(BaseModel):
    total: int
    items: List[LocationResponse]
