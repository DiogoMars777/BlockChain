import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select

from app.models.cu010_ordenes_compra.purchase import Compra, CompraDetalle
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu009_categorias.category import Categoria
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu016_codigos_qr.qr_code import CodigoQR
from app.models.cu019_envios_logisticos.shipment import Envio
from app.models.cu020_asignacion_unidades_envio.shipment_unit import EnvioUnidad
from app.models.cu021_eventos_transporte.transport_event import EventoTrazabilidad, CondicionTransporte
from app.models.cu003_roles_permisos.role import Role
from app.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant

ROL_ADMIN_EMPRESA = "AdministradorEmpresa"


ROLES_GESTION_RECEPCION = ("SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones")
ROL_GESTOR_OPERACIONES = "GestorOperaciones"


def get_auth_header(client, setup_test_data):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "empresa-test-1",
            "email": "user1@test.com",
            "password": "MiClave@123"
        }
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_sprint2_data(db_session, setup_test_data):
    t1 = setup_test_data["tenant1"]
    u1 = setup_test_data["user1"]

    # 1. Proveedor / Actor
    actor_prov = ActorCadena(
        idtenant=t1.idtenant,
        nombre="Apple Distribution USA",
        razonsocial="Apple Operations Inc.",
        tipoactor="PROVEEDOR_EEUU",
        email="orders@apple.com"
    )
    actor_dest = ActorCadena(
        idtenant=t1.idtenant,
        nombre="AlmacÃ©n Central La Paz",
        razonsocial="Importadora Bolivia S.A.",
        tipoactor="IMPORTADOR",
        email="almacen@importadora.bo"
    )
    db_session.add_all([actor_prov, actor_dest])
    db_session.flush()

    # 2. UbicaciÃ³n
    ubicacion = Ubicacion(
        idtenant=t1.idtenant,
        nombre="Aduana Interior La Paz",
        pais="Bolivia",
        ciudad="El Alto",
        tipo="aduana"
    )
    db_session.add(ubicacion)
    db_session.flush()

    # 3. CategorÃ­a, Producto, Variante
    cat = db_session.execute(select(Categoria).where(Categoria.nombrecategoria == "Smartphones")).scalars().first()
    if not cat:
        cat = Categoria(nombrecategoria="Smartphones", descripcion="TelÃ©fonos mÃ³viles")
        db_session.add(cat)
        db_session.flush()

    prod = db_session.execute(select(Producto).where(Producto.nombre == "iPhone 16 Pro Max")).scalars().first()
    if not prod:
        prod = Producto(
            idcategoria=cat.idcategoria,
            nombre="iPhone 16 Pro Max",
            modelo="A3297",
            activo=True
        )
        db_session.add(prod)
        db_session.flush()

    var = db_session.execute(select(VarianteProducto).where(VarianteProducto.sku == "IPH16PM-256-BLK")).scalars().first()
    if not var:
        var = VarianteProducto(
            idproducto=prod.idproducto,
            sku="IPH16PM-256-BLK",
            color="Titanio Negro",
            capacidad="256GB"
        )
        db_session.add(var)
        db_session.flush()

    # 4. Compra (CU-011)
    compra = Compra(
        idtenant=t1.idtenant,
        idproveedor=actor_prov.idactor,
        numeroorden="PO-2026-001",
        fechacompra=date(2026, 9, 15),
        totalusd=Decimal("2398.00"),
        estado="pendiente"
    )
    db_session.add(compra)
    db_session.flush()

    detalle = CompraDetalle(
        idcompra=compra.idcompra,
        idvariante=var.idvariante,
        cantidad=2,
        costounitariousd=Decimal("1199.00"),
        subtotalusd=Decimal("2398.00")
    )
    db_session.add(detalle)
    db_session.flush()

    # 5. Unidad de producto (CU-016)
    unidad = UnidadProducto(
        idtenant=t1.idtenant,
        idvariante=var.idvariante,
        numeroserie="F2LWK0XYZ1",
        imei1="358921102938471",
        estado="disponible"
    )
    db_session.add(unidad)
    db_session.flush()

    # 6. EnvÃ­o (CU-021)
    envio = Envio(
        idtenant=t1.idtenant,
        idactororigen=actor_prov.idactor,
        idactordestino=actor_dest.idactor,
        codigoenvio="ENV-BO-9901",
        estado="preparacion",
        trackingexterno="DHL-88991122"
    )
    db_session.add(envio)
    db_session.flush()

    envio_u = EnvioUnidad(idenvio=envio.idenvio, idunidad=unidad.idunidad)
    db_session.add(envio_u)

    # Rol que habilita aprobar/rechazar compras (CU-011 exige control de acceso por rol)
    rol = db_session.execute(
        select(Role).where(Role.nombrerol == ROL_ADMIN_EMPRESA)
    ).scalar_one_or_none()
    if not rol:
        rol = Role(nombrerol=ROL_ADMIN_EMPRESA, descripcion="Administrador de empresa (test)")
        db_session.add(rol)
        db_session.flush()

    ut1 = db_session.execute(
        select(UsuarioTenant).where(
            UsuarioTenant.idusuario == u1.idusuario,
            UsuarioTenant.idtenant == t1.idtenant,
        )
    ).scalar_one()
    db_session.add(UsuarioTenantRol(idusuariotenant=ut1.idusuariotenant, idrol=rol.idrol))

    db_session.commit()

    return {
        "compra": compra,
        "compra_detalle": detalle,
        "unidad": unidad,
        "envio": envio,
        "ubicacion": ubicacion,
        "actor_prov": actor_prov,
        "actor_dest": actor_dest,
        "rol": rol
    }


# ==================== TESTS CU-011: COMPRAS ====================

def test_list_purchases(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/purchases", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    item = data["items"][0]
    assert item["numeroorden"] == "PO-2026-001"
    assert item["estado"] == "pendiente"
    assert len(item["detalles"]) == 1


def test_approve_purchase_success(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    cid = seed_sprint2_data["compra"].idcompra

    response = client.patch(f"/api/v1/purchases/{cid}/approve", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["compra"]["estado"] == "enviada"
    assert "aprobada exitosamente" in data["message"]

    # Verificar que no se puede volver a aprobar
    repeat_resp = client.patch(f"/api/v1/purchases/{cid}/approve", headers=headers)
    assert repeat_resp.status_code == 400


def test_reject_purchase_with_reason(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    cid = seed_sprint2_data["compra"].idcompra

    # ValidaciÃ³n de motivo mÃ­nimo
    invalid_resp = client.patch(f"/api/v1/purchases/{cid}/reject", headers=headers, json={"motivo": "no"})
    assert invalid_resp.status_code == 422

    # Rechazo exitoso
    response = client.patch(
        f"/api/v1/purchases/{cid}/reject",
        headers=headers,
        json={"motivo": "Precios unitarios no coinciden con la proforma de Apple"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["compra"]["estado"] == "cancelada"


# ==================== TESTS CU-016: CÃ“DIGOS QR ====================

def test_list_units_for_qr(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/qr/units", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    unit = items[0]
    assert unit["numeroserie"] == "F2LWK0XYZ1"


def test_generate_and_render_qr(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    uid = seed_sprint2_data["unidad"].idunidad

    # Generar QR
    gen_resp = client.post(f"/api/v1/qr/generate/{uid}", headers=headers)
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert gen_data["tokenpublico"] is not None
    assert "/trace/" in gen_data["url"]

    # Renderizar imagen QR (PNG)
    img_resp = client.get(f"/api/v1/qr/{uid}/image", headers=headers)
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"] == "image/png"
    assert len(img_resp.content) > 100  # Imagen PNG vÃ¡lida con bytes


def test_generate_bulk_qr(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    uid = seed_sprint2_data["unidad"].idunidad

    response = client.post("/api/v1/qr/generate-bulk", headers=headers, json={"idunidades": [uid]})
    assert response.status_code == 200
    data = response.json()
    assert data["total_generados"] == 1


# ==================== TESTS CU-021: EVENTOS TRANSPORTE ====================

def test_list_shipments(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/shipments", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    assert items[0]["codigoenvio"] == "ENV-BO-9901"
    assert items[0]["total_unidades"] == 1


def test_record_transport_event_with_telemetry(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    sid = seed_sprint2_data["envio"].idenvio
    loc_id = seed_sprint2_data["ubicacion"].idubicacion

    # Registrar hito con telemetrÃ­a ambiental
    body = {
        "tipoevento": "transporte_terrestre",
        "idubicacion": loc_id,
        "descripcion": "Paso por punto de control aduanero Tambo Quemado",
        "condiciones": {
            "temperatura": 18.5,
            "humedad": 44.0,
            "presion": 1012.0,
            "nivelvibracion": 0.25,
            "fuentedatos": "Sensor IoT BLE MÃ³vil"
        }
    }
    response = client.post(f"/api/v1/shipments/{sid}/events", headers=headers, json=body)
    assert response.status_code == 200
    ev = response.json()
    assert ev["tipoevento"] == "transporte_terrestre"
    assert ev["payloadhash"] is not None
    assert float(ev["condiciones"]["temperatura"]) == 18.5

    # Consultar timeline
    timeline_resp = client.get(f"/api/v1/shipments/{sid}/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert timeline["envio"]["estado"] == "en_transito"
    assert len(timeline["eventos"]) == 1
    assert "F2LWK0XYZ1" in timeline["unidades_numeros"]


# ==================== TESTS CU-012: RECEPCIONES DE MERCANCIA ====================


def test_list_receptions_empty(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/receptions", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_reception_completa_genera_unidades(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    cid = seed_sprint2_data["compra"].idcompra
    var_id = seed_sprint2_data["compra_detalle"].idvariante
    loc_id = seed_sprint2_data["ubicacion"].idubicacion

    # La orden debe estar aprobada ('enviada') para admitir la recepcion.
    assert client.patch(f"/api/v1/purchases/{cid}/approve", headers=headers).json()["compra"]["estado"] == "enviada"

    response = client.post(
        "/api/v1/receptions",
        headers=headers,
        json={
            "idcompra": cid,
            "idubicacion": loc_id,
            "numerodocumento": "GR-0001",
            "estado": "completa",
            "detalles": [
                {"idvariante": var_id, "cantidadesperada": 2, "cantidadrecibida": 2}
            ],
        },
    )
    assert response.status_code == 201
    recep = response.json()["recepcion"]
    assert recep["estado"] == "completa"
    assert recep["total_recibido"] == 2
    assert len(recep["detalles"]) == 1
    assert recep["detalles"][0]["unidades_generadas"] == 2

    # La orden queda totalmente recibida.
    compra = client.get(f"/api/v1/purchases/{cid}", headers=headers).json()
    assert compra["estado"] == "recibida_total"

    # Las unidadesfisicas existen y sonè¿½æº¯ de la recepcion.
    unidades = client.get("/api/v1/qr/units", headers=headers).json()
    series = {u["numeroserie"] for u in unidades}
    assert any(s.startswith("REC-GR-0001") for s in series)


def test_create_reception_rechaza_orden_no_aprobada(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    cid = seed_sprint2_data["compra"].idcompra
    var_id = seed_sprint2_data["compra_detalle"].idvariante
    loc_id = seed_sprint2_data["ubicacion"].idubicacion

    response = client.post(
        "/api/v1/receptions",
        headers=headers,
        json={
            "idcompra": cid,
            "idubicacion": loc_id,
            "numerodocumento": "GR-NA",
            "detalles": [
                {"idvariante": var_id, "cantidadesperada": 2, "cantidadrecibida": 1}
            ],
        },
    )
    assert response.status_code == 400
    assert "enviada" in response.json()["detail"]


def test_create_reception_rejects_unknown_variant(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    cid = seed_sprint2_data["compra"].idcompra
    loc_id = seed_sprint2_data["ubicacion"].idubicacion
    client.patch(f"/api/v1/purchases/{cid}/approve", headers=headers)

    response = client.post(
        "/api/v1/receptions",
        headers=headers,
        json={
            "idcompra": cid,
            "idubicacion": loc_id,
            "numerodocumento": "GR-X",
            "detalles": [{"idvariante": 999999, "cantidadesperada": 1, "cantidadrecibida": 1}],
        },
    )
    assert response.status_code == 400
    assert "999999" in response.json()["detail"]


def test_create_reception_rejects_cantidad_sobre_esperada(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    cid = seed_sprint2_data["compra"].idcompra
    var_id = seed_sprint2_data["compra_detalle"].idvariante
    loc_id = seed_sprint2_data["ubicacion"].idubicacion
    client.patch(f"/api/v1/purchases/{cid}/approve", headers=headers)

    response = client.post(
        "/api/v1/receptions",
        headers=headers,
        json={
            "idcompra": cid,
            "idubicacion": loc_id,
            "numerodocumento": "GR-OVER",
            "detalles": [
                {"idvariante": var_id, "cantidadesperada": 2, "cantidadrecibida": 5}
            ],
        },
    )
    assert response.status_code == 400


def test_update_reception_estado_rechazada(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    cid = seed_sprint2_data["compra"].idcompra
    var_id = seed_sprint2_data["compra_detalle"].idvariante
    loc_id = seed_sprint2_data["ubicacion"].idubicacion
    client.patch(f"/api/v1/purchases/{cid}/approve", headers=headers)

    created = client.post(
        "/api/v1/receptions",
        headers=headers,
        json={
            "idcompra": cid,
            "idubicacion": loc_id,
            "numerodocumento": "GR-REC",
            "estado": "parcial",
            "detalles": [
                {"idvariante": var_id, "cantidadesperada": 2, "cantidadrecibida": 1}
            ],
        },
    ).json()["recepcion"]
    rid = created["idrecepcion"]

    # Transicion no permitida: parcial -> pendiente
    bad = client.patch(
        f"/api/v1/receptions/{rid}/estado", headers=headers, json={"estado": "pendiente"}
    )
    assert bad.status_code == 400

    # Mismo estado
    same = client.patch(
        f"/api/v1/receptions/{rid}/estado", headers=headers, json={"estado": "parcial"}
    )
    assert same.status_code == 400

    # Rechazar la recepcion
    ok = client.patch(
        f"/api/v1/receptions/{rid}/estado", headers=headers, json={"estado": "rechazada"}
    )
    assert ok.status_code == 200
    assert ok.json()["recepcion"]["estado"] == "rechazada"

    # Al rechazar, la orden vuelve a 'enviada' y las unidades se retiran.
    assert client.get(f"/api/v1/purchases/{cid}", headers=headers).json()["estado"] == "enviada"
    series = {u["numeroserie"] for u in client.get("/api/v1/qr/units", headers=headers).json()}
    assert not any(s.startswith("REC-GR-REC") for s in series)

    # Estado final: no admite mas transiciones
    final = client.patch(
        f"/api/v1/receptions/{rid}/estado", headers=headers, json={"estado": "completa"}
    )
    assert final.status_code == 400


def test_list_receptions_filtrado_por_estado(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    cid = seed_sprint2_data["compra"].idcompra
    var_id = seed_sprint2_data["compra_detalle"].idvariante
    loc_id = seed_sprint2_data["ubicacion"].idubicacion
    client.patch(f"/api/v1/purchases/{cid}/approve", headers=headers)
    client.post(
        "/api/v1/receptions",
        headers=headers,
        json={
            "idcompra": cid,
            "idubicacion": loc_id,
            "numerodocumento": "GR-F",
            "estado": "parcial",
            "detalles": [
                {"idvariante": var_id, "cantidadesperada": 2, "cantidadrecibida": 1}
            ],
        },
    )

    parciales = client.get("/api/v1/receptions?estado=parcial", headers=headers)
    assert parciales.status_code == 200
    assert len(parciales.json()) == 1
    assert parciales.json()[0]["estado"] == "parcial"

    completas = client.get("/api/v1/receptions?estado=completa", headers=headers)
    assert completas.json() == []

    por_compra = client.get(f"/api/v1/receptions?idcompra={cid}", headers=headers)
    assert len(por_compra.json()) == 1


# ==================== TESTS CU-020: ASIGNACION DE UNIDADES A ENVIOS ====================


def _crear_envio_con_unidades(db_session, tenant, codigo_envio, numero_serie, sku, cantidad=1):
    """Crea un envio en 'preparacion' y N unidades 'disponible' del mismo tenant."""
    actor_prov = db_session.execute(
        select(ActorCadena).where(
            ActorCadena.idtenant == tenant.idtenant,
            ActorCadena.tipoactor == "PROVEEDOR_EEUU",
        )
    ).scalars().first()
    if not actor_prov:
        actor_prov = ActorCadena(
            idtenant=tenant.idtenant,
            nombre=f"Prov {codigo_envio}",
            razonsocial=f"Proveedor {codigo_envio} S.A.",
            tipoactor="PROVEEDOR_EEUU",
            email=f"prov-{codigo_envio}@test.com",
        )
        db_session.add(actor_prov)
        db_session.flush()

    actor_dest = db_session.execute(
        select(ActorCadena).where(
            ActorCadena.idtenant == tenant.idtenant,
            ActorCadena.tipoactor == "IMPORTADOR",
        )
    ).scalars().first()
    if not actor_dest:
        actor_dest = ActorCadena(
            idtenant=tenant.idtenant,
            nombre=f"Dest {codigo_envio}",
            razonsocial=f"Destinatario {codigo_envio} S.A.",
            tipoactor="IMPORTADOR",
            email=f"dest-{codigo_envio}@test.com",
        )
        db_session.add(actor_dest)
        db_session.flush()

    variante = db_session.execute(
        select(VarianteProducto).where(VarianteProducto.sku == sku)
    ).scalars().first()
    if not variante:
        categoria = db_session.execute(
            select(Categoria).where(Categoria.nombrecategoria == "Test CU-020")
        ).scalars().first()
        if not categoria:
            categoria = Categoria(nombrecategoria="Test CU-020", descripcion="Categoria de pruebas CU-020")
            db_session.add(categoria)
            db_session.flush()
        producto = Producto(
            idcategoria=categoria.idcategoria,
            nombre=f"Producto {sku}",
            modelo=f"MOD-{sku}",
            activo=True,
        )
        db_session.add(producto)
        db_session.flush()
        variante = VarianteProducto(
            idproducto=producto.idproducto,
            sku=sku,
            color="Negro",
            capacidad="128GB",
        )
        db_session.add(variante)
        db_session.flush()

    envio = Envio(
        idtenant=tenant.idtenant,
        idactororigen=actor_prov.idactor,
        idactordestino=actor_dest.idactor,
        codigoenvio=codigo_envio,
        estado="preparacion",
    )
    db_session.add(envio)
    db_session.flush()

    unidades = []
    for i in range(1, cantidad + 1):
        serie = numero_serie if cantidad == 1 else f"{numero_serie}-{i:02d}"
        unidad = UnidadProducto(
            idtenant=tenant.idtenant,
            idvariante=variante.idvariante,
            numeroserie=serie,
            estado="disponible",
        )
        db_session.add(unidad)
        db_session.flush()
        unidades.append(unidad)

    db_session.commit()
    return envio.idenvio, unidades


def _asegurar_rol_operaciones(client, setup_test_data, db_session, nombre_rol):
    """Asigna un rol al usuario de prueba para habilitar endpoints con control de acceso."""
    t1 = setup_test_data["tenant1"]
    u1 = setup_test_data["user1"]

    rol = db_session.execute(
        select(Role).where(Role.nombrerol == nombre_rol)
    ).scalar_one_or_none()
    if not rol:
        rol = Role(nombrerol=nombre_rol, descripcion=f"{nombre_rol} (test)")
        db_session.add(rol)
        db_session.flush()

    ut = db_session.execute(
        select(UsuarioTenant).where(
            UsuarioTenant.idusuario == u1.idusuario,
            UsuarioTenant.idtenant == t1.idtenant,
        )
    ).scalar_one()

    ya_asignado = db_session.execute(
        select(UsuarioTenantRol).where(
            UsuarioTenantRol.idusuariotenant == ut.idusuariotenant,
            UsuarioTenantRol.idrol == rol.idrol,
        )
    ).scalar_one_or_none()
    if not ya_asignado:
        db_session.add(
            UsuarioTenantRol(idusuariotenant=ut.idusuariotenant, idrol=rol.idrol)
        )
    db_session.commit()
    return rol


def test_list_shipment_units(client, setup_test_data, seed_sprint2_data):
    headers = get_auth_header(client, setup_test_data)
    sid = seed_sprint2_data["envio"].idenvio

    response = client.get(f"/api/v1/shipments/{sid}/units", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["idenvio"] == sid
    assert data["codigoenvio"] == "ENV-BO-9901"
    assert [u["numeroserie"] for u in data["asignadas"]] == ["F2LWK0XYZ1"]
    # La unidad ya asignada a este envio no debe reaparecer como disponible.
    assert "F2LWK0XYZ1" not in [u["numeroserie"] for u in data["disponibles"]]


def test_assign_unit_to_shipment(client, setup_test_data, db_session):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    _asegurar_rol_operaciones(client, setup_test_data, db_session, ROL_GESTOR_OPERACIONES)
    envio_id, unidades = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-A", "SN-CU020-A", "SKU-CU020")
    uid = unidades[0].idunidad

    before = client.get(f"/api/v1/shipments/{envio_id}/units", headers=headers).json()
    assert [u["numeroserie"] for u in before["asignadas"]] == []

    response = client.post(
        f"/api/v1/shipments/{envio_id}/units", headers=headers, json={"idunidad": uid}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert [u["numeroserie"] for u in data["unidades"]] == ["SN-CU020-A"]

    after = client.get(f"/api/v1/shipments/{envio_id}/units", headers=headers).json()
    assert [u["numeroserie"] for u in after["asignadas"]] == ["SN-CU020-A"]
    assert after["asignadas"][0]["estado"] == "disponible"


def test_assign_unit_twice_is_rejected(client, setup_test_data, db_session):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    _asegurar_rol_operaciones(client, setup_test_data, db_session, ROL_GESTOR_OPERACIONES)
    envio_id, unidades = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-B", "SN-CU020-B", "SKU-B")
    uid = unidades[0].idunidad

    first = client.post(
        f"/api/v1/shipments/{envio_id}/units", headers=headers, json={"idunidad": uid}
    )
    assert first.status_code == 200

    duplicate = client.post(
        f"/api/v1/shipments/{envio_id}/units", headers=headers, json={"idunidad": uid}
    )
    assert duplicate.status_code == 409
    assert "ya esta asignada" in duplicate.json()["detail"]


def test_assign_unit_to_other_shipment_is_rejected(client, setup_test_data, db_session):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    _asegurar_rol_operaciones(client, setup_test_data, db_session, ROL_GESTOR_OPERACIONES)
    envio_a, unidades = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-C1", "SN-CU020-C", "SKU-C")
    envio_b, _ = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-C2", "SN-CU020-OTRA", "SKU-C")
    uid = unidades[0].idunidad

    assert client.post(
        f"/api/v1/shipments/{envio_a}/units", headers=headers, json={"idunidad": uid}
    ).status_code == 200

    conflict = client.post(
        f"/api/v1/shipments/{envio_b}/units", headers=headers, json={"idunidad": uid}
    )
    assert conflict.status_code == 409
    assert "ENV-CU020-C1" in conflict.json()["detail"]


def test_assign_units_bulk(client, setup_test_data, db_session):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    _asegurar_rol_operaciones(client, setup_test_data, db_session, ROL_GESTOR_OPERACIONES)
    envio_id, unidades = _crear_envio_con_unidades(
        db_session, t1, "ENV-CU020-D", "SN-CU020-D", "SKU-D", cantidad=3
    )

    response = client.post(
        f"/api/v1/shipments/{envio_id}/units/bulk",
        headers=headers,
        json={"unidades": [u.idunidad for u in unidades]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["unidades"]) == 3

    after = client.get(f"/api/v1/shipments/{envio_id}/units", headers=headers).json()
    assert len(after["asignadas"]) == 3
    assert after["disponibles"] == []

    # El bulk es atomico: repetirlo con unidades ya asignadas no agrega nada.
    repeat = client.post(
        f"/api/v1/shipments/{envio_id}/units/bulk",
        headers=headers,
        json={"unidades": [u.idunidad for u in unidades]},
    )
    assert repeat.status_code == 409
    assert "ya esta asignada" in repeat.json()["detail"]


def test_unassign_unit_frees_it_for_another_shipment(client, setup_test_data, db_session):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    _asegurar_rol_operaciones(client, setup_test_data, db_session, ROL_GESTOR_OPERACIONES)
    envio_id, unidades = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-E", "SN-CU020-E", "SKU-E")
    uid = unidades[0].idunidad

    assert client.post(
        f"/api/v1/shipments/{envio_id}/units", headers=headers, json={"idunidad": uid}
    ).status_code == 200

    # Desasignar en preparacion deja la unidad libre para otro envio.
    response = client.delete(f"/api/v1/shipments/{envio_id}/units/{uid}", headers=headers)
    assert response.status_code == 200
    assert response.json()["unidades"] == []

    otro_id, _ = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-E2", "SN-CU020-E2", "SKU-E2")
    again = client.post(f"/api/v1/shipments/{otro_id}/units", headers=headers, json={"idunidad": uid})
    assert again.status_code == 200


def test_unassign_unit_blocked_when_shipment_dispatched(client, setup_test_data, db_session):
    """Con el envio ya despachado la mercancia no se puede retirar."""
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    _asegurar_rol_operaciones(client, setup_test_data, db_session, ROL_GESTOR_OPERACIONES)
    envio_id, unidades = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-E3", "SN-CU020-E3", "SKU-E3")
    uid = unidades[0].idunidad

    client.post(f"/api/v1/shipments/{envio_id}/units", headers=headers, json={"idunidad": uid})
    assert client.patch(
        f"/api/v1/shipments/{envio_id}/estado", headers=headers, json={"estado": "en_transito"}
    ).status_code == 200

    blocked = client.delete(f"/api/v1/shipments/{envio_id}/units/{uid}", headers=headers)
    assert blocked.status_code == 400
    assert "preparacion" in blocked.json()["detail"].lower()

    # La unidad sigue asignada al envio.
    data = client.get(f"/api/v1/shipments/{envio_id}/units", headers=headers).json()
    assert [u["numeroserie"] for u in data["asignadas"]] == ["SN-CU020-E3"]


def test_unassign_unit_not_assigned_is_404(client, setup_test_data, db_session):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    _asegurar_rol_operaciones(client, setup_test_data, db_session, ROL_GESTOR_OPERACIONES)
    envio_id, unidades = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-E4", "SN-CU020-E4", "SKU-E4")

    response = client.delete(
        f"/api/v1/shipments/{envio_id}/units/{unidades[0].idunidad}", headers=headers
    )
    assert response.status_code == 404


def test_assign_unit_blocked_when_shipment_not_in_preparacion(
    client, setup_test_data, db_session
):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    _asegurar_rol_operaciones(client, setup_test_data, db_session, ROL_GESTOR_OPERACIONES)
    envio_id, unidades = _crear_envio_con_unidades(db_session, t1, "ENV-CU020-F", "SN-CU020-F", "SKU-F")

    assert client.patch(
        f"/api/v1/shipments/{envio_id}/estado", headers=headers, json={"estado": "en_transito"}
    ).status_code == 200

    response = client.post(
        f"/api/v1/shipments/{envio_id}/units", headers=headers, json={"idunidad": unidades[0].idunidad}
    )
    assert response.status_code == 400
    assert "preparacion" in response.json()["detail"].lower()


def test_assign_unit_from_other_tenant_is_not_visible(client, setup_test_data, db_session):
    """Una unidad de otra empresa nunca aparece como candidata."""
    headers = get_auth_header(client, setup_test_data)
    t2 = setup_test_data["tenant2"]
    envio_id, _ = _crear_envio_con_unidades(db_session, setup_test_data["tenant1"], "ENV-CU020-G", "SN-G", "SKU-G")
    _crear_envio_con_unidades(db_session, t2, "ENV-CU020-G2", "SN-OTRO-TENANT", "SKU-G2")

    data = client.get(f"/api/v1/shipments/{envio_id}/units", headers=headers).json()
    series = {u["numeroserie"] for u in data["disponibles"]}
    assert "SN-OTRO-TENANT" not in series
