from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Esquemas de respuesta JSON para bitácora y notificaciones
class BitacoraResponse(BaseModel):
    idbitacora: int
    idusuariotenant: int
    accion: str
    entidad: str
    identidad: Optional[int] = None
    ip: Optional[str] = None
    fechahora: datetime

    model_config = ConfigDict(from_attributes=True)


class BitacoraListResponse(BaseModel):
    total: int
    items: List[BitacoraResponse]


class NotificacionResponse(BaseModel):
    idnotificacion: int
    idusuariotenant: int
    titulo: str
    contenido: str
    leida: bool
    fechaenvio: datetime
    fechalectura: Optional[datetime] = None
    enlaceaccion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NotificacionListResponse(BaseModel):
    total: int
    unread_count: int
    items: List[NotificacionResponse]
