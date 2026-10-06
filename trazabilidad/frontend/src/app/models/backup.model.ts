export interface TenantBackup {
  idbackup: number;
  idtenant: number;
  idusuario_creador: number;
  nombre_archivo: string;
  cloud_storage: string;
  cloud_path: string;
  peso_bytes: number;
  checksum_sha256?: string;
  estado: 'PENDIENTE' | 'PROCESANDO' | 'COMPLETADO' | 'FALLIDO';
  mensaje_error?: string;
  total_registros: number;
  fechacreacion: string;
}

export interface TenantBackupListResponse {
  total: number;
  items: TenantBackup[];
}

export interface CreateBackupResponse {
  message: string;
  idbackup: number;
  estado: string;
  nombre_archivo: string;
}

export interface DownloadBackupResponse {
  download_url: string;
  nombre_archivo: string;
  modo: 'signed_url' | 'direct';
  expires_in_minutes?: number;
}

export interface BackupSchedule {
  idschedule: number;
  idtenant: number;
  idusuario_creador: number;
  fecha_hora_programada: string;
  frecuencia: 'UNA_VEZ' | 'DIARIO' | 'SEMANAL' | 'MENSUAL';
  activo: boolean;
  estado: 'PROGRAMADO' | 'EJECUTADO' | 'CANCELADO' | 'FALLIDO';
  ultimo_ejecutado?: string;
  proxima_ejecucion?: string;
  mensaje_resultado?: string;
  fechacreacion: string;
}

export interface CreateBackupScheduleRequest {
  fecha_hora_programada: string;
  frecuencia: string;
}

export interface BackupScheduleListResponse {
  total: number;
  items: BackupSchedule[];
}
