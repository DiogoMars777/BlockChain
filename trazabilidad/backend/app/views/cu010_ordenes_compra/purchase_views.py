from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class CompraDetalleCreate(BaseModel):
    idvariante: int = Field(..., description="Variante a ordenar, debe pertenecer al catalogo de la empresa")
    cantidad: int = Field(..., gt=0, description="Cantidad de unidades")
    costounitariousd: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Costo unitario en USD")


class CompraCreate(BaseModel):
    idproveedor: int = Field(..., description="Actor de la cadena con rol de proveedor")
    numeroorden: str = Field(..., min_length=1, max_length=50, description="Numero de orden, unico en el sistema")
    fechacompra: date
    detalles: List[CompraDetalleCreate] = Field(..., min_length=1, description="Al menos una linea de detalle")

    model_config = ConfigDict(from_attributes=True)


class CompraUpdate(BaseModel):
    idproveedor: Optional[int] = None
    numeroorden: Optional[str] = Field(None, min_length=1, max_length=50)
    fechacompra: Optional[date] = None
    detalles: Optional[List[CompraDetalleCreate]] = Field(None, min_length=1)

    model_config = ConfigDict(from_attributes=True)


class CompraDetalleResponse(BaseModel):
    idcompradetalle: int
    idcompra: int
    idvariante: int
    sku: Optional[str] = None
    producto_nombre: Optional[str] = None
    color: Optional[str] = None
    almacenamiento: Optional[str] = None
    cantidad: int
    costounitariousd: Decimal
    subtotalusd: Decimal

    model_config = ConfigDict(from_attributes=True)


class CompraResponse(BaseModel):
    idcompra: int
    idtenant: int
    idproveedor: int
    proveedor_nombre: Optional[str] = None
    numeroorden: str
    fechacompra: date
    totalusd: Decimal
    estado: str
    total_items: Optional[int] = 0
    detalles: Optional[List[CompraDetalleResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class CompraListResponse(BaseModel):
    total: int
    items: List[CompraResponse]