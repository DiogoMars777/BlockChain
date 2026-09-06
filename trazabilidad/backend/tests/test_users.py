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


def test_list_users_authenticated(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] >= 1


def test_create_user_success(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    payload = {
        "nombrecompleto": "Nuevo Operador",
        "email": "operador@test.com",
        "contrasena": "ClaveSegura@123",
        "activo": True
    }
    response = client.post("/api/v1/users", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nombrecompleto"] == "Nuevo Operador"
    assert data["email"] == "operador@test.com"
    assert data["idusuario"] is not None


def test_create_user_duplicate_email(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    payload = {
        "nombrecompleto": "Usuario Repetido",
        "email": "user1@test.com",  # Existing email in setup_test_data
        "contrasena": "ClaveSegura@123"
    }
    response = client.post("/api/v1/users", json=payload, headers=headers)
    assert response.status_code == 400
    assert "correo" in response.json()["detail"]


def test_get_user_by_id(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    u1 = setup_test_data["user1"]
    response = client.get(f"/api/v1/users/{u1.idusuario}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == u1.email


def test_update_user(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    u1 = setup_test_data["user1"]
    payload = {"nombrecompleto": "Usuario Uno Actualizado"}
    response = client.put(f"/api/v1/users/{u1.idusuario}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["nombrecompleto"] == "Usuario Uno Actualizado"


def test_delete_user_soft(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    u2 = setup_test_data["user2"]
    response = client.delete(f"/api/v1/users/{u2.idusuario}", headers=headers)
    assert response.status_code == 200
    assert response.json()["activo"] is False
