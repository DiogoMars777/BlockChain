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


def test_list_roles(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/roles", headers=headers)
    assert response.status_code == 200
    roles = response.json()
    assert isinstance(roles, list)
    assert len(roles) >= 1


def test_list_permissions(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/permissions", headers=headers)
    assert response.status_code == 200
    perms = response.json()
    assert isinstance(perms, list)


def test_get_role_permissions(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/roles/1/permissions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "role" in data
    assert "permissions" in data


def test_get_user_roles(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    u1 = setup_test_data["user1"]
    response = client.get(f"/api/v1/users/{u1.idusuario}/roles", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["idusuario"] == u1.idusuario
    assert isinstance(data["roles"], list)


def test_assign_user_roles(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    u1 = setup_test_data["user1"]
    payload = {"role_ids": [1, 2]}
    response = client.post(f"/api/v1/users/{u1.idusuario}/roles", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["roles"]) == 2
    assigned_ids = [r["idrol"] for r in data["roles"]]
    assert 1 in assigned_ids
    assert 2 in assigned_ids
