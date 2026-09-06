from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class TenantBase(BaseModel):
    nombre: str
    razonsocial: str
    nit: str
    email: EmailStr
    telefono: Optional[str] = None


class TenantCreate(TenantBase):
    activo: Optional[bool] = True


class TenantUpdate(BaseModel):
    nombre: Optional[str] = None
    razonsocial: Optional[str] = None
    nit: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class TenantResponse(BaseModel):
    idtenant: int
    nombre: str
    razonsocial: str
    nit: str
    email: str
    telefono: Optional[str] = None
    activo: Optional[bool] = True
    fechacreacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TenantListResponse(BaseModel):
    total: int
    items: List[TenantResponse]
