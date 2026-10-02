from pydantic import BaseModel, Field

from app.views.cu010_ordenes_compra.purchase_views import CompraResponse


class RejectPurchaseRequest(BaseModel):
    motivo: str = Field(..., min_length=5, max_length=500, description="Motivo justificado del rechazo de la orden de compra")


class ActionPurchaseResponse(BaseModel):
    message: str
    compra: CompraResponse
