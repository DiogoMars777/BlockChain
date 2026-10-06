from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TenantBackupResponse(BaseModel):
    idbackup: int
    idtenant: int
    idusuario_creador: int
    nombre_archivo: str
    cloud_storage: str
    cloud_path: str
    peso_bytes: int
    checksum_sha256: Optional[str] = None
    estado: str
    mensaje_error: Optional[str] = None
    total_registros: int = 0
    fechacreacion: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantBackupListResponse(BaseModel):
    total: int
    items: List[TenantBackupResponse]


class CreateBackupResponse(BaseModel):
    message: str
    idbackup: int
    estado: str
    nombre_archivo: str


class DownloadBackupResponse(BaseModel):
    download_url: str
    nombre_archivo: str
    modo: str  # "signed_url" | "direct"
    expires_in_minutes: Optional[int] = 15


class CreateBackupScheduleRequest(BaseModel):
    fecha_hora_programada: datetime
    frecuencia: Optional[str] = "UNA_VEZ"  # "UNA_VEZ" | "DIARIO" | "SEMANAL" | "MENSUAL"


class BackupScheduleResponse(BaseModel):
    idschedule: int
    idtenant: int
    idusuario_creador: int
    fecha_hora_programada: datetime
    frecuencia: str
    activo: bool
    estado: str
    ultimo_ejecutado: Optional[datetime] = None
    proxima_ejecucion: Optional[datetime] = None
    mensaje_resultado: Optional[str] = None
    fechacreacion: datetime

    model_config = ConfigDict(from_attributes=True)


class BackupScheduleListResponse(BaseModel):
    total: int
    items: List[BackupScheduleResponse]
