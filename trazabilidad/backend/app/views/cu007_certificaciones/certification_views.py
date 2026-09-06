from typing import Optional, List
from datetime import date
from pydantic import BaseModel, ConfigDict


class CertificationCreate(BaseModel):
    nombre: str
    entidademisora: Optional[str] = None
    descripcion: Optional[str] = None
    logourl: Optional[str] = None


class CertificationUpdate(BaseModel):
    nombre: Optional[str] = None
    entidademisora: Optional[str] = None
    descripcion: Optional[str] = None
    logourl: Optional[str] = None


class CertificationResponse(BaseModel):
    idcertificacion: int
    nombre: str
    entidademisora: Optional[str] = None
    descripcion: Optional[str] = None
    logourl: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductCertificationAssign(BaseModel):
    idcertificacion: int
    fechaobtencion: Optional[date] = None


class ProductCertificationResponse(BaseModel):
    idproductocertificacion: int
    idproducto: int
    idcertificacion: int
    fechaobtencion: Optional[date] = None
    certificacion: Optional[CertificationResponse] = None

    model_config = ConfigDict(from_attributes=True)
