import { Component, signal, Signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { TenantService } from '../services/tenant.service';
import { User } from '../../models/auth.models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: '../../views/pages/dashboard.view.html',
  styleUrls: ['../../views/pages/dashboard.view.scss']
})
export class DashboardController implements OnInit {
  private authService = inject(AuthService);
  private tenantService = inject(TenantService);

  currentUser: Signal<User | null> = this.authService.currentUser;
  isLoading = signal(false);
  tenants = this.tenantService.tenantsSignal;

  ngOnInit(): void {
    this.tenantService.getTenants().subscribe();
  }

  onTenantChange(event: Event): void {
    const selectElem = event.target as HTMLSelectElement;
    const tenantId = Number(selectElem.value);
    if (tenantId) {
      this.isLoading.set(true);
      this.authService.switchTenant(tenantId).subscribe({
        next: () => {
          this.isLoading.set(false);
          window.location.reload();
        },
        error: (err) => {
          this.isLoading.set(false);
          alert('Error al cambiar de empresa: ' + (err.error?.detail || 'Intente nuevamente'));
        }
      });
    }
  }

  onLogout(): void {
    this.authService.logout();
  }

  canAccess(module: string): boolean {
    const roles = this.currentUser()?.roles || [];
    if (roles.includes('SuperAdministrador')) {
      return true;
    }

    switch (module) {
      case 'tenants':
        return roles.includes('AdministradorEmpresa');

      case 'users':
      case 'roles':
        return roles.includes('AdministradorEmpresa');

      case 'bitacora':
        return roles.includes('AdministradorEmpresa') || roles.includes('Auditor');

      case 'categories':
      case 'certifications':
      case 'actors':
      case 'locations':
      case 'receptions':
        return roles.includes('AdministradorEmpresa') || roles.includes('GestorOperaciones');

      case 'products':
      case 'tenant-catalog':
      case 'units':
      case 'qr-codes':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('GestorVentasPostventa') ||
          roles.includes('Auditor')
        );

      case 'purchases':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('GestorVentasPostventa')
        );

      case 'shipments':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('Auditor')
        );

      default:
        return false;
    }
  }
}
