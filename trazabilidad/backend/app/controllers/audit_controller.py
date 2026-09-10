"""Backward-compatibility re-export module for CU-005 Bitacora Controller."""
from app.controllers.cu005_bitacora.bitacora_controller import (
    BitacoraController,
    AuditController,
    router,
    get_bitacora,
    get_notifications,
    mark_notification_read
)

__all__ = [
    "BitacoraController",
    "AuditController",
    "router",
    "get_bitacora",
    "get_notifications",
    "mark_notification_read"
]
