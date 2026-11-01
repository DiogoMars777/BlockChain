import pytest
from app.models.cu001_tenants.tenant import Tenant
from app.packages.p1_seguridad.models.cu036_planes.subscription_models import Plan, Suscripcion


def login(client, tenant_slug, email, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"tenant_slug": tenant_slug, "email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# =============================================================================
# PRUEBAS CU-036: GESTIÓN DE PLANES DE SUSCRIPCIÓN
# =============================================================================

def test_listar_planes(client, setup_test_data, auth_headers):
    # Usuario autenticado con rol SuperAdministrador consulta catálogo
    res = client.get("/api/v1/planes", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 4
    codigos = [p["codigo"] for p in data["items"]]
    assert "trial" in codigos
    assert "pro" in codigos


def test_crear_plan_nuevo_y_rechazar_duplicado(client, setup_test_data, auth_headers):
    # Login de user2 que no tiene rol SuperAdministrador asignado
    normal_headers = login(client, "empresa-test-2", "user2@test.com", "OtroPassword@456")

    plan_payload = {
        "codigo": "startup_test",
        "nombre": "Plan Startup Test",
        "descripcion": "Plan especial para pruebas unitarias",
        "preciomensual": "29.99",
        "precioanual": "299.00",
        "moneda": "USD",
        "limiteusuarios": 4,
        "limiteunidades": 50,
        "limitereportesmes": 100,
        "limitealmacenamientomb": 256,
        "diastrial": 7,
        "activo": True
    }

    # Usuario sin rol SuperAdministrador NO puede crear planes (403 Forbidden)
    res_forbidden = client.post("/api/v1/planes", json=plan_payload, headers=normal_headers)
    assert res_forbidden.status_code == 403

    # SuperAdmin crea el plan exitosamente (201 Created)
    res = client.post("/api/v1/planes", json=plan_payload, headers=auth_headers)
    assert res.status_code == 201
    created = res.json()
    assert created["codigo"] == "startup_test"
    plan_id = created["idplan"]

    # Rechazar duplicado con 409 Conflict
    res_dup = client.post("/api/v1/planes", json=plan_payload, headers=auth_headers)
    assert res_dup.status_code == 409

    # Actualizar estado a inactivo
    res_toggle = client.patch(f"/api/v1/planes/{plan_id}/estado", json={"activo": False}, headers=auth_headers)
    assert res_toggle.status_code == 200
    assert res_toggle.json()["activo"] is False


# =============================================================================
# PRUEBAS CU-037: SUSCRIPCIONES Y AISLAMIENTO MULTI-TENANT
# =============================================================================

def test_consultar_suscripcion_actual_tenant(client, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    res = client.get(f"/api/v1/suscripciones/tenant/{t1.idtenant}/actual", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["idtenant"] == t1.idtenant
    assert data["estado"] in ("activa", "trial")
    assert "limites" in data


def test_suscribir_y_cambiar_plan_empresa(client, setup_test_data, auth_headers):
    t2 = setup_test_data["tenant2"]

    # Obtener planes
    res_planes = client.get("/api/v1/planes", headers=auth_headers)
    planes = res_planes.json()["items"]
    plan_basico = next(p for p in planes if p["codigo"] == "basico")
    plan_enterprise = next(p for p in planes if p["codigo"] == "enterprise")

    # SuperAdmin suscribe a Tenant 2 a plan básico
    sub_payload = {
        "idtenant": t2.idtenant,
        "idplan": plan_basico["idplan"],
        "diasvigencia": 60,
        "renovacionautomatica": True
    }
    res_sub = client.post("/api/v1/suscripciones", json=sub_payload, headers=auth_headers)
    assert res_sub.status_code == 201
    sub_data = res_sub.json()
    assert sub_data["idtenant"] == t2.idtenant
    assert sub_data["idplan"] == plan_basico["idplan"]
    assert sub_data["estado"] == "activa"
    sub_id = sub_data["idsuscripcion"]

    # Cambiar de plan a Enterprise (CU-037 cambio de plan)
    change_payload = {
        "nuevoidplan": plan_enterprise["idplan"],
        "diasvigencia": 90,
        "renovacionautomatica": True
    }
    res_change = client.post(f"/api/v1/suscripciones/{sub_id}/cambiar-plan", json=change_payload, headers=auth_headers)
    assert res_change.status_code == 200
    nueva_sub = res_change.json()
    assert nueva_sub["idplan"] == plan_enterprise["idplan"]
    assert nueva_sub["estado"] == "activa"

    # Verificar que la suscripción anterior pasó a cancelada/reemplazada
    res_old = client.get(f"/api/v1/suscripciones/{sub_id}", headers=auth_headers)
    assert res_old.status_code == 200
    assert res_old.json()["estado"] == "cancelada"


def test_suspender_suscripcion(client, setup_test_data, auth_headers):
    res = client.get("/api/v1/suscripciones?estado=activa", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) > 0
    target_id = items[0]["idsuscripcion"]

    patch_payload = {
        "estado": "suspendida",
        "motivocancelacion": "Suspensión administrativa por mora o auditoría"
    }
    res_patch = client.patch(f"/api/v1/suscripciones/{target_id}/estado", json=patch_payload, headers=auth_headers)
    assert res_patch.status_code == 200
    assert res_patch.json()["estado"] == "suspendida"
    assert res_patch.json()["motivocancelacion"] == "Suspensión administrativa por mora o auditoría"
