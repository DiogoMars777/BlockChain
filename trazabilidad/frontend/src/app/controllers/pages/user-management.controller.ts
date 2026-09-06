import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from '../services/user.service';
import { TenantService } from '../services/tenant.service';
import { AuthService } from '../services/auth.service';
import { User, Tenant } from '../../models/auth.models';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: '../../views/pages/user-management.view.html',
  styleUrls: ['../../views/pages/user-management.view.css']
})
export class UserManagementController implements OnInit {
  private userService = inject(UserService);
  private tenantService = inject(TenantService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private fb = inject(FormBuilder);

  currentUser = this.authService.currentUser;
  users = this.userService.usersSignal;
  totalUsers = this.userService.totalUsersSignal;
  isLoading = this.userService.isLoadingSignal;
  tenants = this.tenantService.tenantsSignal;

  searchQuery = signal<string>('');
  selectedTenantFilter = signal<number | null>(null);
  showModal = signal<boolean>(false);
  isEditing = signal<boolean>(false);
  selectedUserId = signal<number | null>(null);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  userForm: FormGroup = this.fb.group({
    nombrecompleto: ['', [Validators.required, Validators.maxLength(100)]],
    email: ['', [Validators.required, Validators.email]],
    contrasena: [''],
    idtenant: [null],
    activo: [true]
  });

  ngOnInit(): void {
    this.loadUsers();
    this.tenantService.getTenants().subscribe();
  }

  loadUsers(): void {
    this.userService.getUsers(this.searchQuery(), this.selectedTenantFilter() || undefined).subscribe({
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cargar los usuarios.');
      }
    });
  }

  onSearchChange(): void {
    this.loadUsers();
  }

  onTenantSwitch(event: Event): void {
    const selectElem = event.target as HTMLSelectElement;
    const tenantId = Number(selectElem.value);
    if (tenantId) {
      this.authService.switchTenant(tenantId).subscribe({
        next: () => {
          this.loadUsers();
        },
        error: (err) => {
          alert('Error al cambiar de empresa: ' + (err.error?.detail || 'Intente nuevamente'));
        }
      });
    }
  }

  openCreateModal(): void {
    this.isEditing.set(false);
    this.selectedUserId.set(null);
    this.userForm.reset({
      nombrecompleto: '',
      email: '',
      contrasena: '',
      idtenant: this.tenants().length > 0 ? this.tenants()[0].idtenant : null,
      activo: true
    });
    this.userForm.get('contrasena')?.setValidators([Validators.required, Validators.minLength(8)]);
    this.userForm.get('contrasena')?.updateValueAndValidity();
    this.errorMessage.set(null);
    this.showModal.set(true);
  }

  openEditModal(user: User): void {
    this.isEditing.set(true);
    this.selectedUserId.set(user.idusuario);
    this.userForm.patchValue({
      nombrecompleto: user.nombrecompleto,
      email: user.email,
      contrasena: '',
      idtenant: user.tenant?.idtenant || null,
      activo: user.activo ?? true
    });
    // Password optional during edit
    this.userForm.get('contrasena')?.clearValidators();
    this.userForm.get('contrasena')?.updateValueAndValidity();
    this.errorMessage.set(null);
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
  }

  onSubmit(): void {
    if (this.userForm.invalid) {
      this.userForm.markAllAsTouched();
      return;
    }

    const formValues = { ...this.userForm.value };
    if (this.isEditing() && !formValues.contrasena) {
      delete formValues.contrasena;
    }

    this.errorMessage.set(null);

    if (this.isEditing() && this.selectedUserId()) {
      this.userService.updateUser(this.selectedUserId()!, formValues).subscribe({
        next: () => {
          this.successMessage.set('Usuario actualizado correctamente.');
          this.closeModal();
          this.loadUsers();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.errorMessage.set(err.error?.detail || 'Error al actualizar el usuario.');
        }
      });
    } else {
      this.userService.createUser(formValues).subscribe({
        next: () => {
          this.successMessage.set('Usuario registrado correctamente.');
          this.closeModal();
          this.loadUsers();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.errorMessage.set(err.error?.detail || 'Error al registrar el usuario.');
        }
      });
    }
  }

  onDelete(user: User): void {
    if (confirm(`¿Estás seguro de desactivar al usuario '${user.nombrecompleto}'?`)) {
      this.userService.deleteUser(user.idusuario).subscribe({
        next: () => {
          this.successMessage.set(`Usuario '${user.nombrecompleto}' desactivado correctamente.`);
          this.loadUsers();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.errorMessage.set(err.error?.detail || 'Error al desactivar el usuario.');
        }
      });
    }
  }

  navigateToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }
}
