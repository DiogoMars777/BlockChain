from app.controllers.cu004_autenticacion.auth_controller import AuthController, router as auth_router, get_current_user
from app.controllers.cu001_tenants.tenant_controller import TenantController, router as tenant_router
from app.controllers.cu002_usuarios.user_controller import UserController, router as user_router
from app.controllers.cu003_roles_permisos.role_controller import RoleController, router as role_router
from app.controllers.cu005_bitacora.bitacora_controller import (
    BitacoraController,
    router as bitacora_router,
    AuditController,
    router as audit_router
)
from app.controllers.cu009_categorias.category_controller import CategoryController, router as category_router
from app.controllers.cu006_productos_variantes.product_controller import ProductController, router as product_router
from app.controllers.cu007_certificaciones.certification_controller import CertificationController, router as certification_router
from app.controllers.cu008_catalogo_empresa.tenant_catalog_controller import TenantCatalogController, router as tenant_catalog_router
from app.controllers.cu013_actores_cadena.actor_controller import ActorController, router as actor_router
from app.controllers.cu014_ubicaciones.location_controller import LocationController, router as location_router
from app.controllers.cu015_unidades_producto.unit_controller import UnitController, router as unit_router

__all__ = [
    "AuthController",
    "auth_router",
    "get_current_user",
    "TenantController",
    "tenant_router",
    "UserController",
    "user_router",
    "RoleController",
    "role_router",
    "AuditController",
    "audit_router",
    "CategoryController",
    "category_router",
    "ProductController",
    "product_router",
    "CertificationController",
    "certification_router",
    "TenantCatalogController",
    "tenant_catalog_router",
    "ActorController",
    "actor_router",
    "LocationController",
    "location_router",
    "UnitController",
    "unit_router",
]
