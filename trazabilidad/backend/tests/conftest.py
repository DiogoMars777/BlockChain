import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.config import settings
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.core.security import hash_password

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh database session for each test and rolls back after test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient fixture with overridden DB dependency."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def setup_test_data(db_session):
    """Sets up Tenant 1, Tenant 2, User 1, and User 2 for testing."""
    t1 = Tenant(nombre="Empresa Test 1", razonsocial="Empresa Test 1 S.A.", nit="1111111", email="test1@empresa.com", activo=True)
    t2 = Tenant(nombre="Empresa Test 2", razonsocial="Empresa Test 2 S.A.", nit="2222222", email="test2@empresa.com", activo=True)
    db_session.add_all([t1, t2])
    db_session.flush()

    u1 = User(
        nombrecompleto="Usuario Uno",
        email="user1@test.com",
        contrasenahash=hash_password("MiClave@123"),
        activo=True
    )
    u2 = User(
        nombrecompleto="Usuario Dos",
        email="user2@test.com",
        contrasenahash=hash_password("OtroPassword@456"),
        activo=True
    )
    db_session.add_all([u1, u2])
    db_session.flush()

    ut1 = UsuarioTenant(idusuario=u1.idusuario, idtenant=t1.idtenant)
    ut2 = UsuarioTenant(idusuario=u2.idusuario, idtenant=t2.idtenant)
    db_session.add_all([ut1, ut2])
    db_session.commit()

    return {"tenant1": t1, "tenant2": t2, "user1": u1, "user2": u2}
