from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.views.cu009_categorias.category_views import CategoryResponse


# Esquemas de Variantes
class VariantCreate(BaseModel):
    capacidad: Optional[str] = None
    color: Optional[str] = None
    sku: str
    preciousd: Decimal


class VariantUpdate(BaseModel):
    capacidad: Optional[str] = None
    color: Optional[str] = None
    sku: Optional[str] = None
    preciousd: Optional[Decimal] = None


class VariantResponse(BaseModel):
    idvariante: int
    idproducto: int
    capacidad: Optional[str] = None
    color: Optional[str] = None
    sku: str
    preciousd: Decimal

    model_config = ConfigDict(from_attributes=True)


# Esquemas de Productos
class ProductCreate(BaseModel):
    nombre: str
    idcategoria: Optional[int] = None
    modelo: Optional[str] = None
    paisorigen: Optional[str] = None
    descripcion: Optional[str] = None
    imagenurl: Optional[str] = None
    activo: Optional[bool] = True


class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    idcategoria: Optional[int] = None
    modelo: Optional[str] = None
    paisorigen: Optional[str] = None
    descripcion: Optional[str] = None
    imagenurl: Optional[str] = None
    activo: Optional[bool] = None


class ProductResponse(BaseModel):
    idproducto: int
    idcategoria: Optional[int] = None
    nombre: str
    modelo: Optional[str] = None
    paisorigen: Optional[str] = None
    descripcion: Optional[str] = None
    imagenurl: Optional[str] = None
    fechacreacion: datetime
    activo: bool
    categoria: Optional[CategoryResponse] = None
    variantes: List[VariantResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]
