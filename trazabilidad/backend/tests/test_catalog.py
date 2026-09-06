import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "123456789",
            "email": "admin@trazabilidad.com",
            "password": "Admin123!"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_and_create_categories(auth_headers):
    resp = client.get("/api/v1/categories", headers=auth_headers)
    assert resp.status_code == 200
    initial_count = len(resp.json())

    unique_suffix = int(time.time() * 1000)
    new_cat = {
        "nombrecategoria": f"Categoría Test {unique_suffix}",
        "descripcion": "Categoría de prueba para test"
    }
    create_resp = client.post("/api/v1/categories", json=new_cat, headers=auth_headers)
    assert create_resp.status_code == 201
    cat_data = create_resp.json()
    assert cat_data["nombrecategoria"] == f"Categoría Test {unique_suffix}"

    resp_after = client.get("/api/v1/categories", headers=auth_headers)
    assert len(resp_after.json()) == initial_count + 1


def test_list_create_and_update_products(auth_headers):
    resp = client.get("/api/v1/products", headers=auth_headers)
    assert resp.status_code == 200

    unique_suffix = int(time.time() * 1000)
    new_prod = {
        "nombre": f"iPad Air {unique_suffix}",
        "modelo": "A2902",
        "paisorigen": "EEUU",
        "descripcion": "iPad Air de prueba",
        "idcategoria": 3
    }
    create_resp = client.post("/api/v1/products", json=new_prod, headers=auth_headers)
    assert create_resp.status_code == 201
    prod_data = create_resp.json()
    idprod = prod_data["idproducto"]

    # Add variant with unique SKU
    new_var = {
        "capacidad": "128GB",
        "color": "Azul Estelar",
        "sku": f"SKU-{unique_suffix}",
        "preciousd": 599.00
    }
    var_resp = client.post(f"/api/v1/products/{idprod}/variants", json=new_var, headers=auth_headers)
    assert var_resp.status_code == 201
    var_data = var_resp.json()
    assert var_data["sku"] == f"SKU-{unique_suffix}"

    # Get product detail
    detail_resp = client.get(f"/api/v1/products/{idprod}", headers=auth_headers)
    assert detail_resp.status_code == 200
    assert len(detail_resp.json()["variantes"]) >= 1
