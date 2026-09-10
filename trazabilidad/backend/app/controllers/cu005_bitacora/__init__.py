from app.controllers.cu005_bitacora.bitacora_controller import (
    BitacoraController,
    AuditController,
    router,
    router as bitacora_router,
    router as audit_router,
)

__all__ = [
    "BitacoraController",
    "AuditController",
    "router",
    "bitacora_router",
    "audit_router",
]
