from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.views.cu001_tenants.tenant_views import TenantResponse


class UserBase(BaseModel):
    email: EmailStr
    nombrecompleto: str


class UserCreate(UserBase):
    contrasena: str
    idtenant: Optional[int] = None
    activo: Optional[bool] = True


class UserUpdate(BaseModel):
    nombrecompleto: Optional[str] = None
    email: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    activo: Optional[bool] = None


class UserResponse(UserBase):
    idusuario: int
    activo: Optional[bool] = True
    fecharegistro: Optional[datetime] = None
    tenant: Optional[TenantResponse] = None

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    total: int
    items: List[UserResponse]
