import os
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

import asyncio
from app.db.session import get_db, engine
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu001_tenants.tenant_backup import TenantBackup
from app.models.cu001_tenants.tenant_backup_schedule import TenantBackupSchedule
from app.models.cu002_usuarios.user import User
from app.models.cu005_bitacora.bitacora import Bitacora
from app.controllers.shared import (
    require_roles,
    get_bolivia_now,
    get_client_ip,
    get_idusuariotenant
)
from app.services.tenant_backup_service import TenantBackupService
from app.services.backup_scheduler import BackupSchedulerService
from app.views.cu001_tenants.backup_views import (
    TenantBackupResponse,
    TenantBackupListResponse,
    CreateBackupResponse,
    DownloadBackupResponse,
    CreateBackupScheduleRequest,
    BackupScheduleResponse,
    BackupScheduleListResponse
)

router = APIRouter(prefix="/backups", tags=["Copias de Seguridad por Tenant (SuperAdministrador)"])

# Solo el SuperAdministrador tiene permisos para esta funcionalidad
solo_superadmin = require_roles("SuperAdministrador")




@router.post("/tenants/{idtenant}", response_model=CreateBackupResponse, status_code=status.HTTP_201_CREATED)
def crear_copia_seguridad_tenant(
    idtenant: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(solo_superadmin)
):
    """
    Genera una copia de seguridad aislada y cifrada para un tenant específico.
    Almacena en Supabase Storage (Nube) o local según la configuración activa.
    Accesible ÚNICAMENTE por el SuperAdministrador.
    """
    # 1. Verificar existencia del tenant
    tenant = db.get(Tenant, idtenant)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La empresa con ID {idtenant} no existe."
        )

    # 2. Crear registro inicial
    backup_rec = TenantBackup(
        idtenant=idtenant,
        idusuario_creador=current_user.idusuario,
        nombre_archivo=f"backup_tenant_{idtenant}_generando.json.gz",
        cloud_storage="supabase",
        cloud_path="",
        estado="PENDIENTE",
        fechacreacion=get_bolivia_now()
    )
    db.add(backup_rec)
    db.commit()
    db.refresh(backup_rec)

    # 3. Registrar en Bitácora de Auditoría (CU-005)
    try:
        idut = get_idusuariotenant(db, current_user)
        db.add(Bitacora(
            idusuariotenant=idut,
            accion="BACKUP_SOLICITADO",
            entidad="TenantBackup",
            identidad=backup_rec.idbackup,
            ip=get_client_ip(request),
            fechahora=get_bolivia_now()
        ))
        db.commit()
    except Exception as audit_err:
        print(f"[Audit Error]: {audit_err}")

    # 4. Procesar extracción, compresión y subida a la nube
    try:
        backup_procesado = TenantBackupService.procesar_backup(db, backup_rec.idbackup)
        return CreateBackupResponse(
            message=f"Copia de seguridad generada con éxito para la empresa '{tenant.nombre}'. Registros respaldados: {backup_procesado.total_registros}.",
            idbackup=backup_procesado.idbackup,
            estado=backup_procesado.estado,
            nombre_archivo=backup_procesado.nombre_archivo,
            total_registros=backup_procesado.total_registros
        )
    except Exception as proc_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar la copia de seguridad: {str(proc_err)}"
        )


@router.get("/tenants/{idtenant}", response_model=TenantBackupListResponse)
def listar_copias_seguridad_tenant(
    idtenant: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(solo_superadmin)
):
    """
    Lista el historial cronológico de copias de seguridad de una empresa.
    Accesible ÚNICAMENTE por el SuperAdministrador.
    """
    tenant = db.get(Tenant, idtenant)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La empresa con ID {idtenant} no existe."
        )

    stmt = (
        select(TenantBackup)
        .where(TenantBackup.idtenant == idtenant)
        .order_by(TenantBackup.fechacreacion.desc())
        .offset(skip)
        .limit(limit)
    )
    items = db.execute(stmt).scalars().all()

    return TenantBackupListResponse(
        total=len(items),
        items=[TenantBackupResponse.model_validate(b) for b in items]
    )


@router.get("/tenants/{idtenant}/{idbackup}/download", response_model=DownloadBackupResponse)
def obtener_enlace_descarga(
    idtenant: int,
    idbackup: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(solo_superadmin)
):
    """
    Genera un enlace seguro (URL firmada de Supabase Storage o enlace directo)
    para descargar el archivo de copia de seguridad .json.gz.
    Accesible ÚNICAMENTE por el SuperAdministrador.
    """
    backup = db.get(TenantBackup, idbackup)
    if not backup or backup.idtenant != idtenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Copia de seguridad no encontrada para esta empresa."
        )

    if backup.estado != "COMPLETADO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La copia de seguridad no está disponible (Estado: {backup.estado})."
        )

    # Registrar descarga en bitácora
    try:
        idut = get_idusuariotenant(db, current_user)
        db.add(Bitacora(
            idusuariotenant=idut,
            accion="BACKUP_DESCARGADO",
            entidad="TenantBackup",
            identidad=backup.idbackup,
            ip=get_client_ip(request),
            fechahora=get_bolivia_now()
        ))
        db.commit()
    except Exception as audit_err:
        print(f"[Audit Download Error]: {audit_err}")

    # Si está en Supabase Storage, generar Signed URL
    if backup.cloud_storage == "supabase":
        signed_url = TenantBackupService.generar_signed_url_supabase(backup.cloud_path, expires_in_seconds=900)
        if signed_url:
            return DownloadBackupResponse(
                download_url=signed_url,
                nombre_archivo=backup.nombre_archivo,
                modo="signed_url",
                expires_in_minutes=15
            )

    # Si está en almacenamiento local o si no se pudo generar signed URL
    return DownloadBackupResponse(
        download_url=f"/api/v1/backups/download-local/{backup.idbackup}",
        nombre_archivo=backup.nombre_archivo,
        modo="direct",
        expires_in_minutes=None
    )


@router.get("/download-local/{idbackup}")
def descargar_archivo_local(
    idbackup: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(solo_superadmin)
):
    """Descarga directa del archivo comprimido cuando está almacenado localmente."""
    backup = db.get(TenantBackup, idbackup)
    if not backup:
        raise HTTPException(status_code=404, detail="Copia de seguridad no encontrada.")

    if not os.path.exists(backup.cloud_path):
        raise HTTPException(status_code=404, detail="El archivo físico no se encuentra en el servidor.")

    return FileResponse(
        path=backup.cloud_path,
        filename=backup.nombre_archivo,
        media_type="application/gzip"
    )


# --- ENDPOINTS DE PROGRAMACIÓN AUTOMÁTICA DE COPIAS ---
@router.post("/tenants/{idtenant}/schedule", response_model=BackupScheduleResponse, status_code=status.HTTP_201_CREATED)
def programar_copia_seguridad(
    idtenant: int,
    data: CreateBackupScheduleRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(solo_superadmin)
):
    """
    Programa una copia de seguridad automática para una fecha y hora determinada,
    con opción de recurrencia (UNA_VEZ, DIARIO, SEMANAL, MENSUAL).
    Accesible ÚNICAMENTE por el SuperAdministrador.
    """
    tenant = db.get(Tenant, idtenant)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La empresa con ID {idtenant} no existe."
        )

    # Asegurar fecha en zona horaria boliviana sin tzinfo naive
    target_dt = data.fecha_hora_programada
    if target_dt.tzinfo is not None:
        target_dt = target_dt.astimezone(timezone(timedelta(hours=-4))).replace(tzinfo=None)

    frecuencia_valida = data.frecuencia.upper() if data.frecuencia else "UNA_VEZ"
    if frecuencia_valida not in ("UNA_VEZ", "DIARIO", "SEMANAL", "MENSUAL"):
        frecuencia_valida = "UNA_VEZ"

    sched = TenantBackupSchedule(
        idtenant=idtenant,
        idusuario_creador=current_user.idusuario,
        fecha_hora_programada=target_dt,
        frecuencia=frecuencia_valida,
        activo=True,
        estado="PROGRAMADO",
        proxima_ejecucion=target_dt,
        fechacreacion=get_bolivia_now()
    )
    db.add(sched)
    db.commit()
    db.refresh(sched)

    # Registrar en bitácora
    try:
        idut = get_idusuariotenant(db, current_user)
        db.add(Bitacora(
            idusuariotenant=idut,
            accion="BACKUP_PROGRAMADO",
            entidad="TenantBackupSchedule",
            identidad=sched.idschedule,
            ip=get_client_ip(request),
            fechahora=get_bolivia_now()
        ))
        db.commit()
    except Exception as audit_err:
        print(f"[Audit Schedule Error]: {audit_err}")

    return BackupScheduleResponse.model_validate(sched)


@router.get("/tenants/{idtenant}/schedule", response_model=BackupScheduleListResponse)
def listar_programaciones_tenant(
    idtenant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(solo_superadmin)
):
    """Lista las programaciones de copias de seguridad de una empresa."""
    stmt = (
        select(TenantBackupSchedule)
        .where(TenantBackupSchedule.idtenant == idtenant)
        .order_by(TenantBackupSchedule.fechacreacion.desc())
    )
    items = db.execute(stmt).scalars().all()
    return BackupScheduleListResponse(
        total=len(items),
        items=[BackupScheduleResponse.model_validate(s) for s in items]
    )


@router.delete("/tenants/{idtenant}/schedule/{idschedule}")
def cancelar_programacion_backup(
    idtenant: int,
    idschedule: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(solo_superadmin)
):
    """Cancela o desactiva una copia de seguridad programada."""
    sched = db.get(TenantBackupSchedule, idschedule)
    if not sched or sched.idtenant != idtenant:
        raise HTTPException(status_code=404, detail="Programación no encontrada.")

    sched.activo = False
    sched.estado = "CANCELADO"
    db.commit()

    try:
        idut = get_idusuariotenant(db, current_user)
        db.add(Bitacora(
            idusuariotenant=idut,
            accion="BACKUP_PROGRAMACION_CANCELADA",
            entidad="TenantBackupSchedule",
            identidad=sched.idschedule,
            ip=get_client_ip(request),
            fechahora=get_bolivia_now()
        ))
        db.commit()
    except Exception as audit_err:
        print(f"[Audit Cancel Schedule Error]: {audit_err}")

    return {"message": f"Programación #{idschedule} cancelada exitosamente."}


@router.post("/tenants/{idtenant}/schedule/{idschedule}/run-now")
def ejecutar_programacion_ahora(
    idtenant: int,
    idschedule: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(solo_superadmin)
):
    """Fuerza la ejecución inmediata de una programación de copia de seguridad."""
    sched = db.get(TenantBackupSchedule, idschedule)
    if not sched or sched.idtenant != idtenant:
        raise HTTPException(status_code=404, detail="Programación no encontrada.")

    try:
        ahora = get_bolivia_now()
        backup_rec = TenantBackup(
            idtenant=sched.idtenant,
            idusuario_creador=current_user.idusuario,
            nombre_archivo=f"backup_auto_tenant_{sched.idtenant}_generando.json.gz",
            cloud_storage="supabase",
            cloud_path="",
            estado="PENDIENTE",
            fechacreacion=ahora
        )
        db.add(backup_rec)
        db.commit()
        db.refresh(backup_rec)

        backup_procesado = TenantBackupService.procesar_backup(db, backup_rec.idbackup)

        sched.ultimo_ejecutado = ahora
        if sched.frecuencia == "UNA_VEZ":
            sched.activo = False
            sched.estado = "EJECUTADO"
            sched.proxima_ejecucion = None
            sched.mensaje_resultado = f"Copia completada (Backup #{backup_procesado.idbackup})"
        elif sched.frecuencia == "DIARIO":
            sched.proxima_ejecucion = ahora + timedelta(days=1)
            sched.mensaje_resultado = f"Copia completada (Backup #{backup_procesado.idbackup})"
        elif sched.frecuencia == "SEMANAL":
            sched.proxima_ejecucion = ahora + timedelta(weeks=1)
            sched.mensaje_resultado = f"Copia completada (Backup #{backup_procesado.idbackup})"
        elif sched.frecuencia == "MENSUAL":
            sched.proxima_ejecucion = ahora + timedelta(days=30)
            sched.mensaje_resultado = f"Copia completada (Backup #{backup_procesado.idbackup})"
        db.commit()

        # Auditoría
        try:
            idut = get_idusuariotenant(db, current_user)
            db.add(Bitacora(
                idusuariotenant=idut,
                accion="BACKUP_AUTOMATICO_MANUAL_RUN",
                entidad="TenantBackupSchedule",
                identidad=sched.idschedule,
                ip=get_client_ip(request),
                fechahora=ahora
            ))
            db.commit()
        except Exception:
            pass

        return {
            "message": f"Copia programada #{idschedule} ejecutada con éxito.",
            "idbackup": backup_procesado.idbackup,
            "total_registros": backup_procesado.total_registros
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al ejecutar: {str(e)}")

