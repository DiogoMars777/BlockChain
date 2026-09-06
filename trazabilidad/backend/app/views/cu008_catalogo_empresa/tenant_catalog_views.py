from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.views.cu006_productos_variantes.product_views import VariantResponse


class TenantCatalogCreate(BaseModel):
    idvariante: int
    idtenant: Optional[int] = None
    skuinterno: Optional[str] = None
    precioventa: Decimal
    costopromedio: Optional[Decimal] = None
    activo: Optional[bool] = True


class TenantCatalogUpdate(BaseModel):
    skuinterno: Optional[str] = None
    precioventa: Optional[Decimal] = None
    costopromedio: Optional[Decimal] = None
    activo: Optional[bool] = None


class TenantCatalogResponse(BaseModel):
    idcatalogotenant: int
    idtenant: int
    idvariante: int
    skuinterno: Optional[str] = None
    precioventa: Decimal
    costopromedio: Optional[Decimal] = None
    activo: bool
    variante: Optional[VariantResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TenantCatalogListResponse(BaseModel):
    total: int
    items: List[TenantCatalogResponse]
