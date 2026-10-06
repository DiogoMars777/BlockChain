import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.cu001_tenants.tenant_backup import TenantBackup
from app.models.cu001_tenants.tenant_backup_schedule import TenantBackupSchedule
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu005_bitacora.bitacora import Bitacora
from app.services.tenant_backup_service import TenantBackupService


def get_bolivia_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)


class BackupSchedulerService:
    _loop_running = False

    @classmethod
    def verificar_y_ejecutar_programaciones(cls):
        """Revisa las tareas programadas cuya fecha/hora ya venció y las ejecuta."""
        db: Session = SessionLocal()
        try:
            ahora = get_bolivia_now()
            # Buscar programaciones activas listas para ejecutarse
            stmt = (
                select(TenantBackupSchedule)
                .where(
                    TenantBackupSchedule.activo == True,
                    TenantBackupSchedule.estado == "PROGRAMADO",
                    TenantBackupSchedule.proxima_ejecucion <= ahora
                )
            )
            pendientes = db.execute(stmt).scalars().all()

            for sched in pendientes:
                print(f"[Scheduler] Ejecutando copia automática #{sched.idschedule} para Tenant #{sched.idtenant}...")
                try:
                    # 1. Crear registro de Backup
                    backup_rec = TenantBackup(
                        idtenant=sched.idtenant,
                        idusuario_creador=sched.idusuario_creador,
                        nombre_archivo=f"backup_auto_tenant_{sched.idtenant}_generando.json.gz",
                        cloud_storage="supabase",
                        cloud_path="",
                        estado="PENDIENTE",
                        fechacreacion=ahora
                    )
                    db.add(backup_rec)
                    db.commit()
                    db.refresh(backup_rec)

                    # 2. Procesar respaldo físico / nube
                    backup_procesado = TenantBackupService.procesar_backup(db, backup_rec.idbackup)

                    # 3. Actualizar la programación según frecuencia
                    sched.ultimo_ejecutado = ahora
                    if sched.frecuencia == "UNA_VEZ":
                        sched.activo = False
                        sched.estado = "EJECUTADO"
                        sched.proxima_ejecucion = None
                        sched.mensaje_resultado = f"Copia automática completada (Backup #{backup_procesado.idbackup})"
                    elif sched.frecuencia == "DIARIO":
                        sched.proxima_ejecucion = sched.proxima_ejecucion + timedelta(days=1)
                        sched.mensaje_resultado = f"Copia diaria completada (Backup #{backup_procesado.idbackup}). Próxima: {sched.proxima_ejecucion}"
                    elif sched.frecuencia == "SEMANAL":
                        sched.proxima_ejecucion = sched.proxima_ejecucion + timedelta(weeks=1)
                        sched.mensaje_resultado = f"Copia semanal completada (Backup #{backup_procesado.idbackup}). Próxima: {sched.proxima_ejecucion}"
                    elif sched.frecuencia == "MENSUAL":
                        sched.proxima_ejecucion = sched.proxima_ejecucion + timedelta(days=30)
                        sched.mensaje_resultado = f"Copia mensual completada (Backup #{backup_procesado.idbackup}). Próxima: {sched.proxima_ejecucion}"

                    # 4. Registrar en Bitácora de Auditoría
                    ut_stmt = select(UsuarioTenant.idusuariotenant).where(
                        UsuarioTenant.idusuario == sched.idusuario_creador,
                        UsuarioTenant.idtenant == sched.idtenant
                    )
                    idut = db.execute(ut_stmt).scalar()
                    if not idut:
                        idut_any = select(UsuarioTenant.idusuariotenant).where(
                            UsuarioTenant.idusuario == sched.idusuario_creador
                        )
                        idut = db.execute(idut_any).scalar()

                    if idut:
                        db.add(Bitacora(
                            idusuariotenant=idut,
                            accion="BACKUP_AUTOMATICO_COMPLETADO",
                            entidad="TenantBackupSchedule",
                            identidad=sched.idschedule,
                            ip="127.0.0.1 (Scheduler)",
                            fechahora=ahora
                        ))

                    db.commit()
                    print(f"[Scheduler] Copia automática #{sched.idschedule} ejecutada con éxito.")

                except Exception as task_err:
                    db.rollback()
                    sched.mensaje_resultado = f"Error al ejecutar: {str(task_err)}"
                    sched.estado = "ERROR" if sched.frecuencia == "UNA_VEZ" else "PROGRAMADO"
                    db.commit()
                    print(f"[Scheduler Error en tarea #{sched.idschedule}]: {task_err}")

        except Exception as e:
            print(f"[Scheduler Global Check Error]: {e}")
        finally:
            db.close()

    @classmethod
    async def start_scheduler_loop(cls):
        """Bucle asíncrono que corre periódicamente en segundo plano dentro de FastAPI."""
        if cls._loop_running:
            return
        cls._loop_running = True
        print("[Scheduler] Motor de copias automáticas iniciado.")

        while True:
            try:
                # Ejecutar verificación cada 30 segundos sin bloquear el event loop
                await asyncio.to_thread(cls.verificar_y_ejecutar_programaciones)
            except Exception as loop_err:
                print(f"[Scheduler Loop Warning]: {loop_err}")

            await asyncio.sleep(30)
