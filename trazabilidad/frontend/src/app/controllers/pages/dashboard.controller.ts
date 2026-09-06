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
}
