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


def test_get_bitacora(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/bitacora", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data


def test_get_notifications(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    response = client.get("/api/v1/notifications", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "unread_count" in data
    assert "items" in data


def test_mark_notification_read(client, setup_test_data):
    headers = get_auth_header(client, setup_test_data)
    # First get notifications to find an ID
    notif_resp = client.get("/api/v1/notifications", headers=headers)
    items = notif_resp.json()["items"]
    if items:
        nid = items[0]["idnotificacion"]
        response = client.patch(f"/api/v1/notifications/{nid}/read", headers=headers)
        assert response.status_code == 200
        assert response.json()["leida"] is True
