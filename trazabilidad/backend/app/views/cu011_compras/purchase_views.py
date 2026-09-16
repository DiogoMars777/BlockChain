from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


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


class RejectPurchaseRequest(BaseModel):
    motivo: str = Field(..., min_length=5, max_length=500, description="Motivo justificado del rechazo de la orden de compra")


class ActionPurchaseResponse(BaseModel):
    message: str
    compra: CompraResponse
