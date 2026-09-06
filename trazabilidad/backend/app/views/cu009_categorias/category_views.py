from typing import Optional
from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    nombrecategoria: str
    descripcion: Optional[str] = None


class CategoryUpdate(BaseModel):
    nombrecategoria: Optional[str] = None
    descripcion: Optional[str] = None


class CategoryResponse(BaseModel):
    idcategoria: int
    nombrecategoria: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
