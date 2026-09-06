from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class RoleResponse(BaseModel):
    idrol: int
    nombrerol: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PermissionResponse(BaseModel):
    idpermiso: int
    nombrepermiso: str
    descripcion: Optional[str] = None
    modulo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RolePermissionsResponse(BaseModel):
    role: RoleResponse
    permissions: List[PermissionResponse]


class AssignUserRolesRequest(BaseModel):
    role_ids: List[int]


class UserRolesResponse(BaseModel):
    idusuario: int
    idusuariotenant: int
    nombrecompleto: str
    roles: List[RoleResponse]
