from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.controllers.cu004_autenticacion.auth_controller import router as auth_router
from app.controllers.cu001_tenants.tenant_controller import router as tenant_router
from app.controllers.cu002_usuarios.user_controller import router as user_router
from app.controllers.cu003_roles_permisos.role_controller import router as role_router
from app.controllers.audit_controller import router as audit_router
from app.controllers.cu009_categorias.category_controller import router as category_router
from app.controllers.cu006_productos_variantes.product_controller import router as product_router
from app.controllers.cu007_certificaciones.certification_controller import router as certification_router
from app.controllers.cu008_catalogo_empresa.tenant_catalog_controller import router as tenant_catalog_router
from app.controllers.cu013_actores_cadena.actor_controller import router as actor_router
from app.controllers.cu014_ubicaciones.location_controller import router as location_router
from app.controllers.cu015_unidades_producto.unit_controller import router as unit_router

app = FastAPI(
    title=settings.APP_NAME,
    description="API Enterprise Multi-Tenant de Trazabilidad en arquitectura MVC",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [i.strip() for i in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Controller routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tenant_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(role_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(certification_router, prefix="/api/v1")
app.include_router(tenant_catalog_router, prefix="/api/v1")
app.include_router(actor_router, prefix="/api/v1")
app.include_router(location_router, prefix="/api/v1")
app.include_router(unit_router, prefix="/api/v1")


from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.db.session import get_db
from sqlalchemy.orm import Session

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=500,
        content={"error_type": type(exc).__name__, "error_detail": str(exc), "trace": traceback.format_exc()}
    )

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1")).scalar()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return {"status": "ok", "app": settings.APP_NAME, "db": db_status}
