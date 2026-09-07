import sys
import os
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu003_roles_permisos.role import Role
from app.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.models.cu009_categorias.category import Categoria
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu007_certificaciones.certification import Certificacion, ProductoCertificacion
from app.models.cu008_catalogo_empresa.tenant_catalog import CatalogoTenant
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.core.security import hash_password, validate_password_strength

DEMO_PASSWORD = os.getenv("SEED_PASSWORD", "Admin123!")

ROLES = [
    ("SuperAdministrador", "Control total sobre la plataforma, gestión de tenants y configuración global"),
    ("AdministradorEmpresa", "Gestión completa de una empresa (tenant): catálogo, usuarios, reportes"),
    ("GestorOperaciones", "Gestión de abastecimiento, inventario (seriales/IMEI), logística y trazabilidad"),
    ("GestorVentasPostventa", "Gestión de ventas, devoluciones, garantías y documentos adjuntos"),
    ("Consumidor", "Consulta de trazabilidad, favoritos y notificaciones (solo sus productos)"),
    ("Auditor", "Acceso de solo lectura a trazabilidad, blockchain y reportes"),
]

CATALOG = [
    ("Smartphones", "Teléfonos inteligentes de gama alta y media", [
        ("Galaxy S24", "SM-S921", "Corea del Sur", [
            ("128GB", "Negro", "DEMO-GS24-128-NEG", "699.00"),
            ("256GB", "Azul", "DEMO-GS24-256-AZU", "799.00"),
        ]),
        ("iPhone 15", "A3090", "China", [
            ("128GB", "Blanco", "DEMO-IP15-128-BLA", "899.00"),
        ]),
    ]),
    ("Accesorios", "Cargadores, fundas y otros accesorios", [
        ("Cargador USB-C 20W", "GAN-20W", "China", [
            ("-", "Blanco", "DEMO-CARG-20W-BLA", "15.00"),
        ]),
        ("Funda Protectora Universal", "FND-UNI", "Vietnam", [
            ("-", "Negro", "DEMO-FUND-UNI-NEG", "9.00"),
        ]),
    ]),
    ("Wearables", "Relojes y auriculares inteligentes", [
        ("Smartwatch Fit 2", "SWF2", "China", [
            ("-", "Negro", "DEMO-SWF2-NEG", "129.00"),
        ]),
        ("Auriculares TWS Pro", "TWS-PRO", "China", [
            ("-", "Blanco", "DEMO-TWS-BLA", "59.00"),
        ]),
    ]),
]

CERTIFICATIONS = [
    ("Homologación ATT Bolivia", "Autoridad de Regulación y Fiscalización de Telecomunicaciones",
     "Certificado oficial de uso de frecuencias radioeléctricas en Bolivia", ["Galaxy S24", "iPhone 15"]),
    ("Certificación RoHS", "Unión Europea",
     "Restricción de sustancias peligrosas en componentes electrónicos", ["Smartwatch Fit 2"]),
]

TENANTS = [
    {
        "idtenant": 1, "nombre": "iStore Bolivia S.A.",
        "razonsocial": "iStore Importaciones y Distribucion S.A.",
        "nit": "123456789", "email": "importadora@bolivia.com", "telefono": "70000000",
        "admin_email": "admin@trazabilidad.com", "ciudad": "La Paz",
    },
    {
        "idtenant": 2, "nombre": "TechImport Santa Cruz S.R.L.",
        "razonsocial": "TechImport Santa Cruz Sociedad de Responsabilidad Limitada",
        "nit": "987654321", "email": "contacto@techimport.com", "telefono": "70111111",
        "admin_email": "admin@techimport.com", "ciudad": "Santa Cruz de la Sierra",
    },
    {
        "idtenant": 3, "nombre": "Andina Digital Ltda.",
        "razonsocial": "Andina Digital Limitada",
        "nit": "456789123", "email": "contacto@andinadigital.com", "telefono": "70222222",
        "admin_email": "admin@andinadigital.com", "ciudad": "Cochabamba",
    },
    {
        "idtenant": 4, "nombre": "ElectroSur Trading S.A.",
        "razonsocial": "ElectroSur Trading Sociedad Anónima",
        "nit": "321654987", "email": "contacto@electrosur.com", "telefono": "70333333",
        "admin_email": "admin@electrosur.com", "ciudad": "El Alto",
    },
    {
        "idtenant": 5, "nombre": "Cochabamba Wireless S.A.",
        "razonsocial": "Cochabamba Wireless Sociedad Anónima",
        "nit": "654987321", "email": "contacto@cochawireless.com", "telefono": "70444444",
        "admin_email": "admin@cochawireless.com", "ciudad": "Sucre",
    },
]


def get_or_create_tenant(db: Session, data: dict) -> Tenant:
    tenant = db.execute(select(Tenant).where(Tenant.idtenant == data["idtenant"])).scalar_one_or_none()
    if tenant:
        return tenant
    tenant = Tenant(
        idtenant=data["idtenant"], nombre=data["nombre"], razonsocial=data["razonsocial"],
        nit=data["nit"], email=data["email"], telefono=data["telefono"], activo=True,
    )
    db.add(tenant)
    db.flush()
    print(f"  Tenant '{tenant.nombre}' creado.")
    return tenant


def get_or_create_admin_user(db: Session, email: str, nombre: str) -> User:
    is_valid, msg = validate_password_strength(DEMO_PASSWORD)
    if not is_valid:
        print(f"Error: SEED_PASSWORD no cumple los requisitos: {msg}")
        sys.exit(1)

    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user:
        user.contrasenahash = hash_password(DEMO_PASSWORD)
        user.activo = True
        return user
    user = User(nombrecompleto=nombre, email=email, contrasenahash=hash_password(DEMO_PASSWORD), activo=True)
    db.add(user)
    db.flush()
    print(f"  Usuario admin '{email}' creado.")
    return user


def ensure_usuario_tenant_rol(db: Session, user: User, tenant: Tenant, role_name: str) -> UsuarioTenant:
    link = db.execute(
        select(UsuarioTenant).where(
            UsuarioTenant.idusuario == user.idusuario, UsuarioTenant.idtenant == tenant.idtenant
        )
    ).scalar_one_or_none()
    if not link:
        link = UsuarioTenant(idusuario=user.idusuario, idtenant=tenant.idtenant)
        db.add(link)
        db.flush()

    role = db.execute(select(Role).where(Role.nombrerol == role_name)).scalar_one_or_none()
    if role:
        existing = db.execute(
            select(UsuarioTenantRol).where(
                UsuarioTenantRol.idusuariotenant == link.idusuariotenant, UsuarioTenantRol.idrol == role.idrol
            )
        ).scalar_one_or_none()
        if not existing:
            db.add(UsuarioTenantRol(idusuariotenant=link.idusuariotenant, idrol=role.idrol))
    return link


def seed_roles(db: Session) -> None:
    for nombre, descripcion in ROLES:
        exists = db.execute(select(Role).where(Role.nombrerol == nombre)).scalar_one_or_none()
        if not exists:
            db.add(Role(nombrerol=nombre, descripcion=descripcion))
    db.flush()
    print(f"  {len(ROLES)} roles del sistema verificados/creados.")


def get_or_create_categoria(db: Session, nombre: str, descripcion: str) -> Categoria:
    cat = db.execute(select(Categoria).where(Categoria.nombrecategoria == nombre)).scalar_one_or_none()
    if cat:
        return cat
    cat = Categoria(nombrecategoria=nombre, descripcion=descripcion)
    db.add(cat)
    db.flush()
    return cat


def get_or_create_producto(db: Session, categoria: Categoria, nombre: str, modelo: str, pais: str) -> Producto:
    prod = db.execute(select(Producto).where(Producto.nombre == nombre)).scalar_one_or_none()
    if prod:
        return prod
    prod = Producto(idcategoria=categoria.idcategoria, nombre=nombre, modelo=modelo, paisorigen=pais, activo=True)
    db.add(prod)
    db.flush()
    return prod


def get_or_create_variante(db: Session, producto: Producto, capacidad: str, color: str, sku: str, precio: str) -> VarianteProducto:
    variante = db.execute(select(VarianteProducto).where(VarianteProducto.sku == sku)).scalar_one_or_none()
    if variante:
        return variante
    variante = VarianteProducto(
        idproducto=producto.idproducto, capacidad=capacidad, color=color, sku=sku, preciousd=Decimal(precio)
    )
    db.add(variante)
    db.flush()
    return variante


def seed_catalog(db: Session) -> dict:
    """Crea el catálogo global (categorías, productos, variantes). Devuelve sku -> VarianteProducto."""
    variantes_por_sku = {}
    for cat_nombre, cat_desc, productos in CATALOG:
        categoria = get_or_create_categoria(db, cat_nombre, cat_desc)
        for prod_nombre, modelo, pais, variantes in productos:
            producto = get_or_create_producto(db, categoria, prod_nombre, modelo, pais)
            for capacidad, color, sku, precio in variantes:
                variantes_por_sku[sku] = get_or_create_variante(db, producto, capacidad, color, sku, precio)
    print(f"  Catálogo global: {len(CATALOG)} categorías, {len(variantes_por_sku)} variantes.")
    return variantes_por_sku


def seed_certifications(db: Session) -> None:
    for nombre, entidad, descripcion, productos_nombres in CERTIFICATIONS:
        cert = db.execute(select(Certificacion).where(Certificacion.nombre == nombre)).scalar_one_or_none()
        if not cert:
            cert = Certificacion(nombre=nombre, entidademisora=entidad, descripcion=descripcion)
            db.add(cert)
            db.flush()
        for prod_nombre in productos_nombres:
            prod = db.execute(select(Producto).where(Producto.nombre == prod_nombre)).scalar_one_or_none()
            if not prod:
                continue
            existing = db.execute(
                select(ProductoCertificacion).where(
                    ProductoCertificacion.idproducto == prod.idproducto,
                    ProductoCertificacion.idcertificacion == cert.idcertificacion,
                )
            ).scalar_one_or_none()
            if not existing:
                db.add(ProductoCertificacion(
                    idproducto=prod.idproducto, idcertificacion=cert.idcertificacion,
                    fechaobtencion=date.today(),
                ))
    print(f"  {len(CERTIFICATIONS)} certificaciones vinculadas a productos.")


def get_or_create_actor(db: Session, tenant: Tenant, nombre: str, tipoactor: str) -> ActorCadena:
    actor = db.execute(
        select(ActorCadena).where(ActorCadena.idtenant == tenant.idtenant, ActorCadena.nombre == nombre)
    ).scalar_one_or_none()
    if actor:
        return actor
    actor = ActorCadena(
        idtenant=tenant.idtenant, nombre=nombre, razonsocial=nombre,
        nit=f"NIT-{tenant.idtenant}-{tipoactor[:3]}", tipoactor=tipoactor,
    )
    db.add(actor)
    db.flush()
    return actor


def get_or_create_ubicacion(db: Session, tenant: Tenant, actor: ActorCadena, nombre: str, ciudad: str, tipo: str) -> Ubicacion:
    ubic = db.execute(
        select(Ubicacion).where(Ubicacion.idtenant == tenant.idtenant, Ubicacion.nombre == nombre)
    ).scalar_one_or_none()
    if ubic:
        return ubic
    ubic = Ubicacion(
        idtenant=tenant.idtenant, idactor=actor.idactor, nombre=nombre,
        direccion=f"Av. Principal, {ciudad}", ciudad=ciudad, pais="Bolivia", tipo=tipo,
    )
    db.add(ubic)
    db.flush()
    return ubic


def get_or_create_catalogo_tenant(db: Session, tenant: Tenant, variante: VarianteProducto, precio_venta: str) -> CatalogoTenant:
    entry = db.execute(
        select(CatalogoTenant).where(
            CatalogoTenant.idtenant == tenant.idtenant, CatalogoTenant.idvariante == variante.idvariante
        )
    ).scalar_one_or_none()
    if entry:
        return entry
    entry = CatalogoTenant(
        idtenant=tenant.idtenant, idvariante=variante.idvariante,
        skuinterno=f"INT-{tenant.idtenant}-{variante.sku}",
        precioventa=Decimal(precio_venta), costopromedio=Decimal(precio_venta) * Decimal("0.8"), activo=True,
    )
    db.add(entry)
    db.flush()
    return entry


def get_or_create_unidad(db: Session, tenant: Tenant, variante: VarianteProducto, numero_serie: str,
                          custodio: ActorCadena, ubicacion: Ubicacion, con_imei: bool) -> None:
    existing = db.execute(
        select(UnidadProducto).where(
            UnidadProducto.idtenant == tenant.idtenant, UnidadProducto.numeroserie == numero_serie
        )
    ).scalar_one_or_none()
    if existing:
        return
    unidad = UnidadProducto(
        idtenant=tenant.idtenant, idvariante=variante.idvariante, numeroserie=numero_serie,
        imei1=f"35{tenant.idtenant}{variante.idvariante}00000001" if con_imei else None,
        idcustodioactual=custodio.idactor, idubicacionactual=ubicacion.idubicacion, estado="disponible",
    )
    db.add(unidad)


def seed_tenant_operations(db: Session, tenant_data: dict, tenant: Tenant, variantes_por_sku: dict) -> None:
    """Actores, ubicaciones, catálogo por empresa y unidades: datos minimos por tenant."""
    proveedor = get_or_create_actor(db, tenant, f"Proveedor {tenant.nombre}", "DISTRIBUIDOR")
    tienda = get_or_create_actor(db, tenant, f"Tienda {tenant.nombre} Centro", "TIENDA")

    almacen = get_or_create_ubicacion(db, tenant, proveedor, "Almacén Principal", tenant_data["ciudad"], "almacen")
    punto_venta = get_or_create_ubicacion(db, tenant, tienda, "Tienda Centro", tenant_data["ciudad"], "punto_venta")

    skus_tenant = ["DEMO-GS24-128-NEG", "DEMO-IP15-128-BLA", "DEMO-SWF2-NEG"]
    for i, sku in enumerate(skus_tenant):
        variante = variantes_por_sku[sku]
        precio_venta = str(variante.preciousd + Decimal("50.00"))
        get_or_create_catalogo_tenant(db, tenant, variante, precio_venta)
        get_or_create_unidad(
            db, tenant, variante, f"DEMO-{tenant.idtenant}-SN-{i + 1:03d}",
            custodio=tienda, ubicacion=almacen if i % 2 == 0 else punto_venta,
            con_imei=sku != "DEMO-SWF2-NEG",
        )


def run_seed():
    db: Session = SessionLocal()
    try:
        print("Sembrando roles del sistema...")
        seed_roles(db)

        print("Sembrando catálogo global (categorías, productos, variantes)...")
        variantes_por_sku = seed_catalog(db)

        print("Sembrando certificaciones...")
        seed_certifications(db)

        print("Sembrando empresas de demostración...")
        for tenant_data in TENANTS:
            tenant = get_or_create_tenant(db, tenant_data)
            admin = get_or_create_admin_user(db, tenant_data["admin_email"], "Administrador General")
            ensure_usuario_tenant_rol(db, admin, tenant, "AdministradorEmpresa")
            seed_tenant_operations(db, tenant_data, tenant, variantes_por_sku)
            print(f"  '{tenant.nombre}' (tenant_slug={tenant.idtenant}, admin={tenant_data['admin_email']}) listo.")

        db.commit()
        print("\nSEED ejecutado correctamente.")
        print(f"Contraseña de todos los admins de demo: {DEMO_PASSWORD}")

    except Exception as e:
        db.rollback()
        print(f"Error al ejecutar el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
