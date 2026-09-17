import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select

from app.models.cu011_compras.purchase import Compra, CompraDetalle
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu009_categorias.category import Categoria
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu016_codigos_qr.qr_code import CodigoQR
from app.models.cu021_eventos_transporte.shipment import Envio, EnvioUnidad, EventoTrazabilidad, CondicionTransporte


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
        nombre="Almacén Central La Paz",
        razonsocial="Importadora Bolivia S.A.",
        tipoactor="IMPORTADOR",
        email="almacen@importadora.bo"
    )
    db_session.add_all([actor_prov, actor_dest])
    db_session.flush()

    # 2. Ubicación
    ubicacion = Ubicacion(
        idtenant=t1.idtenant,
        nombre="Aduana Interior La Paz",
        pais="Bolivia",
        ciudad="El Alto",
        tipo="aduana"
    )
    db_session.add(ubicacion)
    db_session.flush()

    # 3. Categoría, Producto, Variante
    cat = db_session.execute(select(Categoria).where(Categoria.nombrecategoria == "Smartphones")).scalars().first()
    if not cat:
        cat = Categoria(nombrecategoria="Smartphones", descripcion="Teléfonos móviles")
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

    # 6. Envío (CU-021)
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
    db_session.commit()

    return {
        "compra": compra,
        "unidad": unidad,
        "envio": envio,
        "ubicacion": ubicacion,
        "actor_prov": actor_prov,
        "actor_dest": actor_dest
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

    # Validación de motivo mínimo
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


# ==================== TESTS CU-016: CÓDIGOS QR ====================

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
    assert len(img_resp.content) > 100  # Imagen PNG válida con bytes


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

    # Registrar hito con telemetría ambiental
    body = {
        "tipoevento": "transporte_terrestre",
        "idubicacion": loc_id,
        "descripcion": "Paso por punto de control aduanero Tambo Quemado",
        "condiciones": {
            "temperatura": 18.5,
            "humedad": 44.0,
            "presion": 1012.0,
            "nivelvibracion": 0.25,
            "fuentedatos": "Sensor IoT BLE Móvil"
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
