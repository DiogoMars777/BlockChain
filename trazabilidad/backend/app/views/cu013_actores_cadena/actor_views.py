from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ActorCreate(BaseModel):
    nombre: str
    razonsocial: Optional[str] = None
    nit: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    tipoactor: str


class ActorUpdate(BaseModel):
    nombre: Optional[str] = None
    razonsocial: Optional[str] = None
    nit: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    tipoactor: Optional[str] = None


class ActorResponse(BaseModel):
    idactor: int
    idtenant: int
    nombre: str
    razonsocial: Optional[str] = None
    nit: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    tipoactor: str

    model_config = ConfigDict(from_attributes=True)


class ActorListResponse(BaseModel):
    total: int
    items: List[ActorResponse]
