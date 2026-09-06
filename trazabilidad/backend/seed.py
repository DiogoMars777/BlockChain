import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.core.security import hash_password, validate_password_strength


def run_seed():
    db: Session = SessionLocal()
    try:
        # 1. Ensure Tenant 'Importadora Bolivia S.A.' exists
        stmt_tenant = select(Tenant).where(Tenant.idtenant == 1)
        tenant = db.execute(stmt_tenant).scalar_one_or_none()
        if not tenant:
            tenant = Tenant(
                idtenant=1,
                nombre="Importadora Bolivia S.A.",
                razonsocial="Importadora Bolivia Sociedad Anónima",
                nit="123456789",
                email="importadora@bolivia.com",
                telefono="70000000",
                activo=True
            )
            db.add(tenant)
            db.flush()
            print("Tenant 'Importadora Bolivia S.A.' creado exitosamente.")
        else:
            print(f"Tenant existente: '{tenant.nombre}' (ID: {tenant.idtenant}).")

        # 2. Ensure User 'admin@trazabilidad.com' exists with valid hash
        email = "admin@trazabilidad.com"
        stmt_user = select(User).where(User.email == email)
        user = db.execute(stmt_user).scalar_one_or_none()

        password = os.getenv("SEED_PASSWORD", "Admin123.")
        is_valid, msg = validate_password_strength(password)
        if not is_valid:
            print(f"Error: La contraseña no cumple los requisitos: {msg}")
            sys.exit(1)

        if not user:
            user = User(
                nombrecompleto="Administrador General",
                email=email,
                contrasenahash=hash_password(password),
                activo=True
            )
            db.add(user)
            db.flush()
            print(f"Usuario '{email}' creado exitosamente.")
        else:
            user.contrasenahash = hash_password(password)
            user.activo = True
            print(f"Usuario '{email}' actualizado exitosamente con contraseña válida.")

        # 3. Ensure UsuarioTenant link exists
        stmt_link = select(UsuarioTenant).where(
            UsuarioTenant.idusuario == user.idusuario,
            UsuarioTenant.idtenant == tenant.idtenant
        )
        link = db.execute(stmt_link).scalar_one_or_none()
        if not link:
            link = UsuarioTenant(
                idusuario=user.idusuario,
                idtenant=tenant.idtenant
            )
            db.add(link)
            print(f"Vínculo UsuarioTenant creado entre User {user.idusuario} y Tenant {tenant.idtenant}.")
        else:
            print("Vínculo UsuarioTenant ya existe.")

        db.commit()
        print("SEED ejecutado correctamente con las tablas del cliente.")

    except Exception as e:
        db.rollback()
        print(f"Error al ejecutar el seed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
