from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.db.session import get_db
from app.models.cu003_roles_permisos.role import Role
from app.models.cu003_roles_permisos.permission import Permiso
from app.models.cu003_roles_permisos.role_permission import RolPermiso
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.models.cu002_usuarios.user import User
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.views.cu003_roles_permisos.role_views import (
    RoleResponse,
    PermissionResponse,
    RolePermissionsResponse,
    AssignUserRolesRequest,
    UserRolesResponse
)

router = APIRouter(tags=["Asignación de Roles y Permisos (CU-003)"])


class RoleController:
    @staticmethod
    def list_roles(db: Session) -> List[RoleResponse]:
        stmt = select(Role).order_by(Role.idrol.asc())
        roles = db.execute(stmt).scalars().all()
        return [RoleResponse.model_validate(r) for r in roles]

    @staticmethod
    def list_permissions(db: Session) -> List[PermissionResponse]:
        stmt = select(Permiso).order_by(Permiso.modulo.asc(), Permiso.idpermiso.asc())
        perms = db.execute(stmt).scalars().all()
        return [PermissionResponse.model_validate(p) for p in perms]

    @staticmethod
    def get_role_permissions(db: Session, idrol: int) -> RolePermissionsResponse:
        stmt_r = select(Role).where(Role.idrol == idrol)
        role = db.execute(stmt_r).scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con ID {idrol} no encontrado."
            )

        stmt_p = (
            select(Permiso)
            .join(RolPermiso, RolPermiso.idpermiso == Permiso.idpermiso)
            .where(RolPermiso.idrol == idrol)
        )
        perms = db.execute(stmt_p).scalars().all()

        return RolePermissionsResponse(
            role=RoleResponse.model_validate(role),
            permissions=[PermissionResponse.model_validate(p) for p in perms]
        )

    @staticmethod
    def get_user_roles(db: Session, idusuario: int, current_user: User) -> UserRolesResponse:
        # 1. Fetch user
        stmt_u = select(User).where(User.idusuario == idusuario)
        user = db.execute(stmt_u).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {idusuario} no encontrado."
            )

        # 2. Fetch usuariotenant record
        stmt_ut = select(UsuarioTenant).where(UsuarioTenant.idusuario == idusuario)
        ut = db.execute(stmt_ut).scalars().first()
        if not ut:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El usuario con ID {idusuario} no está asignado a ninguna empresa."
            )

        # 3. Fetch user's assigned roles
        stmt_r = (
            select(Role)
            .join(UsuarioTenantRol, UsuarioTenantRol.idrol == Role.idrol)
            .where(UsuarioTenantRol.idusuariotenant == ut.idusuariotenant)
        )
        roles = db.execute(stmt_r).scalars().all()

        return UserRolesResponse(
            idusuario=user.idusuario,
            idusuariotenant=ut.idusuariotenant,
            nombrecompleto=user.nombrecompleto,
            roles=[RoleResponse.model_validate(r) for r in roles]
        )

    @staticmethod
    def assign_user_roles(
        db: Session,
        idusuario: int,
        data: AssignUserRolesRequest,
        current_user: User
    ) -> UserRolesResponse:
        # 1. Fetch user
        stmt_u = select(User).where(User.idusuario == idusuario)
        user = db.execute(stmt_u).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {idusuario} no encontrado."
            )

        # 2. Fetch usuariotenant record
        stmt_ut = select(UsuarioTenant).where(UsuarioTenant.idusuario == idusuario)
        ut = db.execute(stmt_ut).scalars().first()
        if not ut:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El usuario con ID {idusuario} no está asignado a ninguna empresa."
            )

        # 3. Validate role IDs
        if data.role_ids:
            stmt_valid = select(Role.idrol).where(Role.idrol.in_(data.role_ids))
            valid_ids = db.execute(stmt_valid).scalars().all()
            invalid_ids = set(data.role_ids) - set(valid_ids)
            if invalid_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Los siguientes IDs de rol no existen: {list(invalid_ids)}"
                )

        # 4. Remove existing roles for this user tenant link
        db.execute(
            delete(UsuarioTenantRol).where(UsuarioTenantRol.idusuariotenant == ut.idusuariotenant)
        )

        # 5. Insert new roles
        for rid in set(data.role_ids):
            utr = UsuarioTenantRol(idusuariotenant=ut.idusuariotenant, idrol=rid)
            db.add(utr)

        db.commit()

        # 6. Return updated user roles
        return RoleController.get_user_roles(db, idusuario, current_user)


# Endpoints
@router.get("/roles", response_model=List[RoleResponse])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todos los roles del sistema (CU-003)."""
    return RoleController.list_roles(db)


@router.get("/permissions", response_model=List[PermissionResponse])
def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todos los permisos del sistema (CU-003)."""
    return RoleController.list_permissions(db)


@router.get("/roles/{idrol}/permissions", response_model=RolePermissionsResponse)
def get_role_permissions(
    idrol: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consultar permisos de un rol específico (CU-003)."""
    return RoleController.get_role_permissions(db, idrol)


@router.get("/users/{idusuario}/roles", response_model=UserRolesResponse)
def get_user_roles(
    idusuario: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consultar los roles asignados a un usuario (CU-003)."""
    return RoleController.get_user_roles(db, idusuario, current_user)


@router.post("/users/{idusuario}/roles", response_model=UserRolesResponse)
def assign_user_roles(
    idusuario: int,
    data: AssignUserRolesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Asignar/Reemplazar roles a un usuario (CU-003)."""
    return RoleController.assign_user_roles(db, idusuario, data, current_user)
