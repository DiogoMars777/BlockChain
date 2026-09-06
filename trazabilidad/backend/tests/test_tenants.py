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


def test_list_tenants_authenticated(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/tenants", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] >= 2


def test_create_tenant_success(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    payload = {
        "nombre": "Nueva Empresa Corp",
        "razonsocial": "Nueva Empresa Corp S.R.L.",
        "nit": "999888777",
        "email": "contacto@nuevaempresa.com",
        "telefono": "78912345",
        "activo": True
    }
    response = client.post("/api/v1/tenants", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Nueva Empresa Corp"
    assert data["nit"] == "999888777"
    assert data["idtenant"] is not None


def test_create_tenant_duplicate_nit(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    payload = {
        "nombre": "Empresa Duplicada",
        "razonsocial": "Empresa Duplicada S.A.",
        "nit": "1111111",  # Existing NIT in setup_test_data
        "email": "dup@empresa.com"
    }
    response = client.post("/api/v1/tenants", json=payload, headers=headers)
    assert response.status_code == 400
    assert "NIT" in response.json()["detail"]


def test_get_tenant_by_id(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    response = client.get(f"/api/v1/tenants/{t1.idtenant}", headers=headers)
    assert response.status_code == 200
    assert response.json()["nombre"] == t1.nombre


def test_update_tenant(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]
    payload = {"nombre": "Empresa Test 1 Modificada", "telefono": "77700000"}
    response = client.put(f"/api/v1/tenants/{t1.idtenant}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Empresa Test 1 Modificada"
    assert response.json()["telefono"] == "77700000"


def test_delete_tenant_soft(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    t2 = setup_test_data["tenant2"]
    response = client.delete(f"/api/v1/tenants/{t2.idtenant}", headers=headers)
    assert response.status_code == 200
    assert response.json()["activo"] is False
