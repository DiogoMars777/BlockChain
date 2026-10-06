export interface RecommendationMetric {
  vendidas?: number;
  disponibles?: number;
  devueltas?: number;
  pedidas?: number;
  recibidas?: number;
  precioventa?: number;
  costopromedio?: number;
  margen_pct?: number;
  margen_abs_usd?: number;
  rotacion_mensual?: number;
  devolucion_pct?: number;
  brecha_demanda?: number;
  precio_sugerido_usd?: number | null;
}

export interface PricingRecommendationItem {
  idvariante: number;
  sku?: string | null;
  producto?: string | null;
  capacidad?: string | null;
  color?: string | null;
  tipo: string;
  prioridad: 'critica' | 'alta' | 'media' | 'baja' | string;
  titulo: string;
  justificacion: string;
  accion_sugerida: string;
  metricas: RecommendationMetric;
  evidencia: string[];
}

export interface PricingRecommendationsResponse {
  tenant_id: number;
  generated_at: string;
  total_recomendaciones: number;
  recomendaciones: PricingRecommendationItem[];
}

export interface PricingRecommendationRequest {
  top_n?: number;
  tenant_id?: number;
}
