from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class RecommendationMetric(BaseModel):
    vendidas: Optional[int] = 0
    disponibles: Optional[int] = 0
    devueltas: Optional[int] = 0
    pedidas: Optional[int] = 0
    recibidas: Optional[int] = 0
    precioventa: Optional[float] = 0.0
    costopromedio: Optional[float] = 0.0
    margen_pct: Optional[float] = 0.0
    margen_abs_usd: Optional[float] = 0.0
    rotacion_mensual: Optional[float] = 0.0
    devolucion_pct: Optional[float] = 0.0
    brecha_demanda: Optional[int] = 0
    precio_sugerido_usd: Optional[float] = None


class PricingRecommendationItem(BaseModel):
    idvariante: int
    sku: Optional[str] = None
    producto: Optional[str] = None
    capacidad: Optional[str] = None
    color: Optional[str] = None
    tipo: str
    prioridad: str
    titulo: str
    justificacion: str
    accion_sugerida: str
    metricas: RecommendationMetric
    evidencia: List[str] = []


class PricingRecommendationsResponse(BaseModel):
    tenant_id: int
    generated_at: str
    total_recomendaciones: int
    recomendaciones: List[PricingRecommendationItem]


class PricingRecommendationRequest(BaseModel):
    top_n: Optional[int] = 8
    tenant_id: Optional[int] = None
    model_config = ConfigDict(extra="forbid")
