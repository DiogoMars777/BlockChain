from datetime import datetime, timezone, timedelta


def get_superadmin_header(client, setup_test_data):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "empresa-test-1",
            "email": "user1@test.com",
            "password": "MiClave@123"
        }
    )
    token = login_resp.json()["access_token"]
    init_headers = {"Authorization": f"Bearer {token}"}

    u1 = setup_test_data["user1"]
    client.post(f"/api/v1/users/{u1.idusuario}/roles", json={"role_ids": [1]}, headers=init_headers)

    login_resp2 = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "empresa-test-1",
            "email": "user1@test.com",
            "password": "MiClave@123"
        }
    )
    token2 = login_resp2.json()["access_token"]
    return {"Authorization": f"Bearer {token2}"}


def test_manual_backup_creation_and_listing(client, setup_test_data):
    headers = get_superadmin_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]

    # 1. Crear backup manual
    resp = client.post(f"/api/v1/backups/tenants/{t1.idtenant}", headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["idbackup"] is not None
    assert data["estado"] == "COMPLETADO"
    assert data["total_registros"] >= 1
    assert "backup_tenant_" in data["nombre_archivo"]

    # 2. Listar backups
    list_resp = client.get(f"/api/v1/backups/tenants/{t1.idtenant}", headers=headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert any(b["idbackup"] == data["idbackup"] for b in list_data["items"])


def test_backup_download_url(client, setup_test_data):
    headers = get_superadmin_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]

    # Crear backup
    create_resp = client.post(f"/api/v1/backups/tenants/{t1.idtenant}", headers=headers)
    assert create_resp.status_code == 201
    idbackup = create_resp.json()["idbackup"]

    # Solicitar descarga
    dl_resp = client.get(f"/api/v1/backups/tenants/{t1.idtenant}/{idbackup}/download", headers=headers)
    assert dl_resp.status_code == 200
    dl_data = dl_resp.json()
    assert "download_url" in dl_data
    assert dl_data["nombre_archivo"].endswith(".json.gz")


def test_backup_scheduler_flow(client, setup_test_data):
    headers = get_superadmin_header(client, setup_test_data)
    t1 = setup_test_data["tenant1"]

    # 1. Crear programación
    target_dt = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    sched_payload = {
        "fecha_hora_programada": target_dt,
        "frecuencia": "DIARIO"
    }
    create_sched = client.post(f"/api/v1/backups/tenants/{t1.idtenant}/schedule", json=sched_payload, headers=headers)
    assert create_sched.status_code == 201
    sched_data = create_sched.json()
    assert sched_data["idschedule"] is not None
    assert sched_data["frecuencia"] == "DIARIO"
    assert sched_data["activo"] is True
    assert sched_data["estado"] == "PROGRAMADO"

    idsched = sched_data["idschedule"]

    # 2. Listar programaciones
    list_sched = client.get(f"/api/v1/backups/tenants/{t1.idtenant}/schedule", headers=headers)
    assert list_sched.status_code == 200
    assert any(s["idschedule"] == idsched for s in list_sched.json()["items"])

    # 3. Forzar ejecución inmediata (run-now)
    run_now = client.post(f"/api/v1/backups/tenants/{t1.idtenant}/schedule/{idsched}/run-now", headers=headers)
    assert run_now.status_code == 200
    run_data = run_now.json()
    assert "idbackup" in run_data
    assert run_data["total_registros"] >= 1

    # 4. Cancelar programación
    cancel_resp = client.delete(f"/api/v1/backups/tenants/{t1.idtenant}/schedule/{idsched}", headers=headers)
    assert cancel_resp.status_code == 200

    # Verificar que quedó inactiva
    list_after = client.get(f"/api/v1/backups/tenants/{t1.idtenant}/schedule", headers=headers)
    sched_updated = next(s for s in list_after.json()["items"] if s["idschedule"] == idsched)
    assert sched_updated["activo"] is False
    assert sched_updated["estado"] == "CANCELADO"
