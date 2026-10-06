import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { TenantService } from '../services/tenant.service';
import { AuthService } from '../services/auth.service';
import { BackupService } from '../services/backup.service';
import { Tenant } from '../../models/auth.models';
import { TenantBackup, BackupSchedule } from '../../models/backup.model';

@Component({
  selector: 'app-tenant-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: '../../views/pages/tenant-management.view.html',
  styleUrls: ['../../views/pages/tenant-management.view.css']
})
export class TenantManagementController implements OnInit {
  private tenantService = inject(TenantService);
  private authService = inject(AuthService);
  private backupService = inject(BackupService);
  private router = inject(Router);
  private fb = inject(FormBuilder);

  currentUser = this.authService.currentUser;
  tenants = this.tenantService.tenantsSignal;
  totalTenants = this.tenantService.totalTenantsSignal;
  isLoading = this.tenantService.isLoadingSignal;
  isSwitching = signal<boolean>(false);

  searchQuery = signal<string>('');
  showModal = signal<boolean>(false);
  isEditing = signal<boolean>(false);
  selectedTenantId = signal<number | null>(null);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  // Estados para Copias de Seguridad (Backups)
  showBackupModal = signal<boolean>(false);
  activeBackupTab = signal<'history' | 'schedule'>('history');
  selectedBackupTenant = signal<Tenant | null>(null);
  backups = this.backupService.backupsSignal;
  isLoadingBackups = this.backupService.isLoadingSignal;
  isGeneratingBackup = this.backupService.isGeneratingSignal;
  backupFeedback = signal<string | null>(null);

  // Estados para Programación Automática de Copias
  schedules = signal<BackupSchedule[]>([]);
  isLoadingSchedules = signal<boolean>(false);
  isSavingSchedule = signal<boolean>(false);
  scheduleDateTime = signal<string>('');
  scheduleFrequency = signal<string>('UNA_VEZ');

  tenantForm: FormGroup = this.fb.group({
    nombre: ['', [Validators.required, Validators.maxLength(100)]],
    razonsocial: ['', [Validators.required, Validators.maxLength(100)]],
    nit: ['', [Validators.required, Validators.maxLength(50)]],
    email: ['', [Validators.required, Validators.email]],
    telefono: ['', [Validators.maxLength(20)]],
    activo: [true]
  });

  ngOnInit(): void {
    this.loadTenants();
  }

  loadTenants(): void {
    this.tenantService.getTenants(this.searchQuery()).subscribe({
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cargar las empresas.');
      }
    });
  }

  onSearchChange(): void {
    this.loadTenants();
  }

  openCreateModal(): void {
    this.isEditing.set(false);
    this.selectedTenantId.set(null);
    this.tenantForm.reset({
      nombre: '',
      razonsocial: '',
      nit: '',
      email: '',
      telefono: '',
      activo: true
    });
    this.errorMessage.set(null);
    this.showModal.set(true);
  }

  openEditModal(tenant: Tenant): void {
    this.isEditing.set(true);
    this.selectedTenantId.set(tenant.idtenant);
    this.tenantForm.patchValue({
      nombre: tenant.nombre,
      razonsocial: tenant.razonsocial,
      nit: tenant.nit,
      email: tenant.email,
      telefono: tenant.telefono || '',
      activo: tenant.activo ?? true
    });
    this.errorMessage.set(null);
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
  }

  onSubmit(): void {
    if (this.tenantForm.invalid) {
      this.tenantForm.markAllAsTouched();
      return;
    }

    const formValues = this.tenantForm.value;
    this.errorMessage.set(null);

    if (this.isEditing() && this.selectedTenantId()) {
      this.tenantService.updateTenant(this.selectedTenantId()!, formValues).subscribe({
        next: () => {
          this.successMessage.set('Empresa actualizada correctamente.');
          this.closeModal();
          this.loadTenants();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.errorMessage.set(err.error?.detail || 'Error al actualizar la empresa.');
        }
      });
    } else {
      this.tenantService.createTenant(formValues).subscribe({
        next: () => {
          this.successMessage.set('Empresa registrada correctamente.');
          this.closeModal();
          this.loadTenants();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.errorMessage.set(err.error?.detail || 'Error al registrar la empresa.');
        }
      });
    }
  }

  onDelete(tenant: Tenant): void {
    if (confirm(`¿Estás seguro de desactivar la empresa '${tenant.nombre}'?`)) {
      this.tenantService.deleteTenant(tenant.idtenant).subscribe({
        next: () => {
          this.successMessage.set(`Empresa '${tenant.nombre}' desactivada correctamente.`);
          this.loadTenants();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.errorMessage.set(err.error?.detail || 'Error al desactivar la empresa.');
        }
      });
    }
  }

  switchToTenant(tenant: Tenant): void {
    if (this.currentUser()?.tenant?.idtenant === tenant.idtenant) {
      this.router.navigate(['/dashboard']);
      return;
    }

    this.isSwitching.set(true);
    this.successMessage.set(`Cambiando al entorno de '${tenant.nombre}'...`);
    this.errorMessage.set(null);

    this.authService.switchTenant(tenant.idtenant).subscribe({
      next: () => {
        this.isSwitching.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.isSwitching.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al cambiar a esta empresa.');
        this.successMessage.set(null);
      }
    });
  }

  navigateToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }

  // --- MÉTODOS DE COPIAS DE SEGURIDAD (SUPERADMIN) ---
  openBackupModal(tenant: Tenant): void {
    this.selectedBackupTenant.set(tenant);
    this.activeBackupTab.set('history');
    this.backupFeedback.set(null);
    this.showBackupModal.set(true);

    // Sugerir fecha/hora por defecto (1 hora en el futuro) para el input datetime-local
    const future = new Date(Date.now() + 60 * 60 * 1000);
    future.setMinutes(future.getMinutes() - future.getTimezoneOffset());
    this.scheduleDateTime.set(future.toISOString().slice(0, 16));

    this.loadBackups(tenant.idtenant);
    this.loadSchedules(tenant.idtenant);
  }

  closeBackupModal(): void {
    this.showBackupModal.set(false);
    this.selectedBackupTenant.set(null);
    this.backupFeedback.set(null);
  }

  setBackupTab(tab: 'history' | 'schedule'): void {
    this.activeBackupTab.set(tab);
    this.backupFeedback.set(null);
  }

  loadBackups(idtenant: number): void {
    this.backupService.getBackups(idtenant).subscribe({
      error: (err) => {
        this.backupFeedback.set(err.error?.detail || 'Error al obtener las copias de seguridad.');
      }
    });
  }

  triggerBackup(): void {
    const tenant = this.selectedBackupTenant();
    if (!tenant) return;

    this.backupFeedback.set(null);
    this.backupService.createBackup(tenant.idtenant).subscribe({
      next: (res) => {
        this.backupFeedback.set(`✅ ${res.message} (Registros: ${res.total_registros})`);
        this.loadBackups(tenant.idtenant);
      },
      error: (err) => {
        this.backupFeedback.set(err.error?.detail || 'Error al generar la copia de seguridad.');
      }
    });
  }

  downloadBackup(backup: TenantBackup): void {
    if (backup.estado !== 'COMPLETADO') return;

    this.backupService.getDownloadUrl(backup.idtenant, backup.idbackup).subscribe({
      next: (res) => {
        this.backupService.downloadFileDirectly(res.download_url, res.nombre_archivo);
      },
      error: (err) => {
        this.backupFeedback.set(err.error?.detail || 'Error al generar el enlace de descarga.');
      }
    });
  }

  // --- MÉTODOS DE PROGRAMACIÓN AUTOMÁTICA ---
  loadSchedules(idtenant: number): void {
    this.isLoadingSchedules.set(true);
    this.backupService.getSchedules(idtenant).subscribe({
      next: (res) => {
        this.schedules.set(res.items);
        this.isLoadingSchedules.set(false);
      },
      error: (err) => {
        this.isLoadingSchedules.set(false);
        this.backupFeedback.set(err.error?.detail || 'Error al cargar las programaciones.');
      }
    });
  }

  createSchedule(): void {
    const tenant = this.selectedBackupTenant();
    if (!tenant) return;

    if (!this.scheduleDateTime()) {
      this.backupFeedback.set('⚠️ Por favor especifique fecha y hora para la copia automática.');
      return;
    }

    const isoDate = new Date(this.scheduleDateTime()).toISOString();
    this.isSavingSchedule.set(true);
    this.backupFeedback.set(null);

    this.backupService.createSchedule(tenant.idtenant, {
      fecha_hora_programada: isoDate,
      frecuencia: this.scheduleFrequency() as any
    }).subscribe({
      next: (created) => {
        this.isSavingSchedule.set(false);
        this.backupFeedback.set(`✅ Programación #${created.idschedule} configurada con éxito (${created.frecuencia}).`);
        this.loadSchedules(tenant.idtenant);
      },
      error: (err) => {
        this.isSavingSchedule.set(false);
        this.backupFeedback.set(err.error?.detail || 'Error al crear la programación de copia.');
      }
    });
  }

  cancelSchedule(sched: BackupSchedule): void {
    if (!confirm(`¿Desea cancelar la programación #${sched.idschedule}?`)) return;

    this.backupService.cancelSchedule(sched.idtenant, sched.idschedule).subscribe({
      next: () => {
        this.backupFeedback.set(`Programación #${sched.idschedule} cancelada.`);
        this.loadSchedules(sched.idtenant);
      },
      error: (err) => {
        this.backupFeedback.set(err.error?.detail || 'Error al cancelar la programación.');
      }
    });
  }

  runScheduleNow(sched: BackupSchedule): void {
    this.backupFeedback.set(`⏳ Ejecutando programación #${sched.idschedule} ahora mismo...`);
    this.backupService.runScheduleNow(sched.idtenant, sched.idschedule).subscribe({
      next: (res) => {
        this.backupFeedback.set(`✅ ${res.message} (Backup #${res.idbackup}, ${res.total_registros} registros)`);
        this.loadSchedules(sched.idtenant);
        this.loadBackups(sched.idtenant);
      },
      error: (err) => {
        this.backupFeedback.set(err.error?.detail || 'Error al forzar la ejecución de la copia.');
      }
    });
  }

  formatBytes(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
