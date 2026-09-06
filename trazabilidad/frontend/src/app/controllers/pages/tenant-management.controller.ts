import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { TenantService } from '../services/tenant.service';
import { AuthService } from '../services/auth.service';
import { Tenant } from '../../models/auth.models';

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
  private router = inject(Router);
  private fb = inject(FormBuilder);

  tenants = this.tenantService.tenantsSignal;
  totalTenants = this.tenantService.totalTenantsSignal;
  isLoading = this.tenantService.isLoadingSignal;

  searchQuery = signal<string>('');
  showModal = signal<boolean>(false);
  isEditing = signal<boolean>(false);
  selectedTenantId = signal<number | null>(null);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

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

  navigateToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }
}
