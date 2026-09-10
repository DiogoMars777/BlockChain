from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.db.session import get_db
from app.models.cu002_usuarios.user import User
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.core.security import hash_password, validate_password_strength
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.views.cu002_usuarios.user_views import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)
from app.views.cu001_tenants.tenant_views import TenantResponse

router = APIRouter(prefix="/users", tags=["Gestión de Usuarios (CU-002)"])


class UserController:
    @staticmethod
    def _build_user_response(db: Session, user: User) -> UserResponse:
        stmt_t = select(Tenant).join(
            UsuarioTenant, UsuarioTenant.idtenant == Tenant.idtenant
        ).where(UsuarioTenant.idusuario == user.idusuario)
        tenant = db.execute(stmt_t).scalars().first()

        return UserResponse(
            idusuario=user.idusuario,
            nombrecompleto=user.nombrecompleto,
            email=user.email,
            activo=user.activo,
            fecharegistro=user.fecharegistro,
            tenant=TenantResponse.model_validate(tenant) if tenant else None
        )

    @staticmethod
    def list_users(
        db: Session,
        current_user: User,
        search: Optional[str] = None,
        tenant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> UserListResponse:
        # Determinar contexto de empresa objetivo
        target_tenant_id = tenant_id
        if target_tenant_id is None:
            if hasattr(current_user, 'tenant') and current_user.tenant:
                target_tenant_id = current_user.tenant.idtenant
            else:
                stmt_tenant_link = select(UsuarioTenant.idtenant).where(
                    UsuarioTenant.idusuario == current_user.idusuario
                )
                target_tenant_id = db.execute(stmt_tenant_link).scalars().first()

        query = select(User).distinct()

        # Filtrar por empresa salvo que target_tenant_id sea -1 (mostrar todo)
        if target_tenant_id and target_tenant_id != -1:
            query = query.join(UsuarioTenant, UsuarioTenant.idusuario == User.idusuario).where(UsuarioTenant.idtenant == target_tenant_id)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(User.nombrecompleto).like(term),
                    func.lower(User.email).like(term)
                )
            )

        # Contar total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.execute(count_stmt).scalar_one()

        # Ejecutar consulta paginada
        query = query.order_by(User.idusuario.asc()).offset(skip).limit(limit)
        users = db.execute(query).scalars().all()

        result_items = [UserController._build_user_response(db, u) for u in users]

        return UserListResponse(total=total, items=result_items)

    @staticmethod
    def create_user(
        db: Session,
        current_user: User,
        data: UserCreate
    ) -> UserResponse:
        email_clean = data.email.strip().lower()

        # 1. Validar correo único
        stmt_existing = select(User).where(func.lower(User.email) == email_clean)
        if db.execute(stmt_existing).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un usuario registrado con el correo '{data.email}'."
            )

        # 2. Validar robustez de la contraseña
        is_valid, msg = validate_password_strength(data.contrasena)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

        # 3. ID de empresa objetivo
        target_tenant_id = data.idtenant
        if not target_tenant_id:
            stmt_link = select(UsuarioTenant.idtenant).where(
                UsuarioTenant.idusuario == current_user.idusuario
            )
            target_tenant_id = db.execute(stmt_link).scalar()

        if not target_tenant_id:
            target_tenant_id = 1  # Respaldo a empresa por defecto 1

        user = User(
            nombrecompleto=data.nombrecompleto.strip(),
            email=email_clean,
            contrasenahash=hash_password(data.contrasena),
            activo=data.activo if data.activo is not None else True
        )
        db.add(user)
        db.flush()

        # 4. Vincular usuario a la empresa
        link = UsuarioTenant(idusuario=user.idusuario, idtenant=target_tenant_id)
        db.add(link)

        db.commit()
        db.refresh(user)

        return UserController._build_user_response(db, user)

    @staticmethod
    def get_user(db: Session, idusuario: int) -> UserResponse:
        stmt = select(User).where(User.idusuario == idusuario)
        user = db.execute(stmt).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {idusuario} no encontrado."
            )

        return UserController._build_user_response(db, user)

    @staticmethod
    def update_user(db: Session, idusuario: int, data: UserUpdate) -> UserResponse:
        stmt = select(User).where(User.idusuario == idusuario)
        user = db.execute(stmt).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {idusuario} no encontrado."
            )

        if data.email and data.email.strip().lower() != user.email:
            email_clean = data.email.strip().lower()
            stmt_email = select(User).where(
                func.lower(User.email) == email_clean,
                User.idusuario != idusuario
            )
            if db.execute(stmt_email).scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro usuario registrado con el correo '{data.email}'."
                )
            user.email = email_clean

        if data.nombrecompleto is not None:
            user.nombrecompleto = data.nombrecompleto.strip()

        if data.contrasena and data.contrasena.strip():
            is_valid, msg = validate_password_strength(data.contrasena)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=msg
                )
            user.contrasenahash = hash_password(data.contrasena)

        if data.activo is not None:
            user.activo = data.activo

        db.commit()
        db.refresh(user)

        return UserController._build_user_response(db, user)

    @staticmethod
    def delete_user(db: Session, idusuario: int) -> UserResponse:
        stmt = select(User).where(User.idusuario == idusuario)
        user = db.execute(stmt).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {idusuario} no encontrado."
            )

        user.activo = False
        db.commit()
        db.refresh(user)

        return UserController._build_user_response(db, user)


# Rutas HTTP
@router.get("", response_model=UserListResponse)
def get_users(
    search: Optional[str] = Query(None, description="Buscador por nombre o correo"),
    tenant_id: Optional[int] = Query(None, description="Filtrar por empresa especifica"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar usuarios del sistema (CU-002)."""
    return UserController.list_users(db, current_user, search, tenant_id, skip, limit)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar un nuevo usuario en el sistema (CU-002)."""
    return UserController.create_user(db, current_user, data)


@router.get("/{idusuario}", response_model=UserResponse)
def get_user_by_id(
    idusuario: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener los detalles de un usuario por su ID (CU-002)."""
    return UserController.get_user(db, idusuario)


@router.put("/{idusuario}", response_model=UserResponse)
def update_user(
    idusuario: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar información de un usuario existente (CU-002)."""
    return UserController.update_user(db, idusuario, data)


@router.delete("/{idusuario}", response_model=UserResponse)
def delete_user(
    idusuario: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desactivación lógica de un usuario (CU-002)."""
    return UserController.delete_user(db, idusuario)
