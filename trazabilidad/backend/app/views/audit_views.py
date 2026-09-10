"""Módulo de reexportación para compatibilidad de vistas de Bitácora (CU-005)."""
from app.views.cu005_bitacora.bitacora_views import (
    BitacoraResponse,
    BitacoraListResponse,
    NotificacionResponse,
    NotificacionListResponse,
)

__all__ = [
    "BitacoraResponse",
    "BitacoraListResponse",
    "NotificacionResponse",
    "NotificacionListResponse",
]
