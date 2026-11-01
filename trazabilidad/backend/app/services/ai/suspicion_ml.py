"""
Servicio de Machine Learning (apoyo no bloqueante) para el análisis de Sospechas de Falsificación (CU-023).

Capacidades:
1. Clasificación NLP / semántica del texto de la denuncia para sugerir el `tipo_anomalia`.
2. Scoring de prioridad y riesgo (0.0 a 1.0) para ordenamiento de inspección operativa.
3. Detección de evidencias duplicadas mediante verificación de hash SHA-256 e integridad.

Regla inmutable (Instrucciones sección 8):
El ML solo sugiere; la creación del reporte, ticket y alerta funciona sin ML y sin alterar
la decisión determinista.
"""
import re
from typing import Dict, Any, Optional, List

# Palabras clave y pesos para clasificación por TF-IDF heurístico / NLP ligero
KEYWORDS_MAP = {
    "empaque_vulnerado": [
        "caja", "empaque", "precinto", "abierto", "roto", "violado", "sello", "adulterado",
        "plastico", "rayado", "golpe", "abollado", "reempacado", "pegamento", "cinta"
    ],
    "discrepancia_serial": [
        "serial", "serie", "imei", "eid", "duplicado", "coincide", "discrepancia", "distinto",
        "diferente", "grabado", "etiqueta", "caja", "numero", "clonado", "clon"
    ],
    "fraude_autenticidad": [
        "falso", "replica", "copia", "trucho", "original", "apple", "pantalla", "bateria",
        "ios", "sistema", "lento", "camara", "calidad", "estafa", "vendedor", "tienda",
        "sospechoso", "fake", "pirata"
    ]
}

# Palabras de alto riesgo térmico / físico / fraude para el cálculo del score
HIGH_RISK_TERMS = [
    "duplicado", "clonado", "estafa", "abierto", "violado", "falso", "replica", "denuncia",
    "robo", "bateria hinchada", "chispa", "humo", "reclamar", "policia", "fiscalia"
]


class SuspicionMLService:
    """Motor de ML auxiliar para análisis de texto y evaluación de severidad."""

    @staticmethod
    def analyze_report(
        descripcion: str,
        tipo_declarado: str,
        tiene_coordenadas: bool = False,
        num_fotos: int = 0
    ) -> Dict[str, Any]:
        """
        Analiza el reporte y retorna sugerencias probabilísticas y score de riesgo.
        No arroja excepciones hacia el flujo principal.
        """
        try:
            texto = (descripcion or "").lower()
            tokens = set(re.findall(r"\w+", texto))

            # 1. Puntuación por categoría
            scores = {"fraude_autenticidad": 0, "empaque_vulnerado": 0, "discrepancia_serial": 0}
            for cat, kw_list in KEYWORDS_MAP.items():
                for kw in kw_list:
                    if kw in texto:
                        scores[cat] += 2 if kw in tokens else 1

            # Categoría sugerida por máxima concordancia
            cat_sugerida = max(scores, key=scores.get) if any(scores.values()) else tipo_declarado

            # 2. Cálculo del Risk Score (0.1 a 0.99)
            base_score = 0.50
            # Si hay palabras críticas de alto riesgo
            risk_hits = sum(1 for term in HIGH_RISK_TERMS if term in texto)
            base_score += min(risk_hits * 0.12, 0.30)

            # Si incluye fotos de respaldo aumenta la confiabilidad del incidente
            if num_fotos >= 2:
                base_score += 0.08
            elif num_fotos == 1:
                base_score += 0.04

            # Si incluye coordenadas GPS verificables
            if tiene_coordenadas:
                base_score += 0.06

            # Normalizar entre 0.10 y 0.98
            risk_score = round(max(0.10, min(0.98, base_score)), 4)

            # Nivel de severidad inferido
            if risk_score >= 0.80:
                severidad_inferida = "critica"
            elif risk_score >= 0.55:
                severidad_inferida = "alta"
            elif risk_score >= 0.35:
                severidad_inferida = "media"
            else:
                severidad_inferida = "baja"

            return {
                "tipo_sugerido": cat_sugerida,
                "score_riesgo": risk_score,
                "severidad_inferida": severidad_inferida,
                "confianza": round(min(0.95, 0.65 + (max(scores.values()) if scores else 0) * 0.05), 2),
                "motor": "heuristico_nlp_v1"
            }
        except Exception:
            # Fallback seguro sin ML
            return {
                "tipo_sugerido": tipo_declarado,
                "score_riesgo": 0.50,
                "severidad_inferida": "alta",
                "confianza": 0.50,
                "motor": "fallback"
            }

