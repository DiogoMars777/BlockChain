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


def test_certifications_crud(auth_headers):
    # List
    resp = client.get("/api/v1/certifications", headers=auth_headers)
    assert resp.status_code == 200

    # Create
    unique_suffix = int(time.time() * 1000)
    new_cert = {
        "nombre": f"ISO-{unique_suffix}",
        "entidademisora": "International Organization for Standardization",
        "descripcion": "Certificación ISO de calidad"
    }
    create_resp = client.post("/api/v1/certifications", json=new_cert, headers=auth_headers)
    assert create_resp.status_code == 201
    cert_data = create_resp.json()
    assert cert_data["nombre"] == f"ISO-{unique_suffix}"
    idcert = cert_data["idcertificacion"]

    # Assign to Product 1
    assign_resp = client.post(
        "/api/v1/products/1/certifications",
        json={"idcertificacion": idcert, "fechaobtencion": "2026-01-15"},
        headers=auth_headers
    )
    assert assign_resp.status_code == 201

    # List product certs
    list_p_certs = client.get("/api/v1/products/1/certifications", headers=auth_headers)
    assert list_p_certs.status_code == 200
    assert len(list_p_certs.json()) >= 1


def test_tenant_catalog_operations(auth_headers):
    # List catalog
    resp = client.get("/api/v1/tenant-catalog", headers=auth_headers)
    assert resp.status_code == 200
    assert "items" in resp.json()

    # Add variant to tenant catalog
    unique_suffix = int(time.time() * 1000)
    # First create a product with valid idcategoria and modelo
    prod_resp = client.post(
        "/api/v1/products",
        json={"nombre": f"Producto Tenant {unique_suffix}", "modelo": "MOD-TEST", "idcategoria": 1},
        headers=auth_headers
    )
    assert prod_resp.status_code == 201
    idprod = prod_resp.json()["idproducto"]

    var_resp = client.post(
        f"/api/v1/products/{idprod}/variants",
        json={"sku": f"SKU-T-{unique_suffix}", "preciousd": 100.00},
        headers=auth_headers
    )
    assert var_resp.status_code == 201
    idvar = var_resp.json()["idvariante"]

    # Add to catalog
    cat_item = {
        "idvariante": idvar,
        "skuinterno": f"INT-SKU-{unique_suffix}",
        "precioventa": 150.00,
        "costopromedio": 90.00
    }
    add_resp = client.post("/api/v1/tenant-catalog", json=cat_item, headers=auth_headers)
    assert add_resp.status_code == 201
    added_data = add_resp.json()
    assert str(added_data["precioventa"]) == "150.00"
