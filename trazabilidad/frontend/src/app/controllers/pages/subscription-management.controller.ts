import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { SubscriptionService } from '../services/subscription.service';
import { TenantService } from '../services/tenant.service';
import { AuthService } from '../services/auth.service';
import { Plan, Suscripcion, SuscribirEmpresaRequest, CambiarPlanRequest, UpdateSuscripcionEstadoRequest } from '../../models/subscription.model';
import { Tenant } from '../../models/auth.models';

@Component({
  selector: 'app-subscription-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: '../../views/pages/subscription-management.view.html',
  styleUrls: ['../../views/pages/subscription-management.view.css']
})
export class SubscriptionManagementController implements OnInit {
  private subscriptionService = inject(SubscriptionService);
  private tenantService = inject(TenantService);
  private authService = inject(AuthService);

  currentUser = this.authService.currentUser;
  planes = this.subscriptionService.planesSignal;
  suscripciones = this.subscriptionService.suscripcionesSignal;
  miSuscripcion = this.subscriptionService.miSuscripcionSignal;
  isLoading = this.subscriptionService.isLoadingSignal;
  tenants = this.tenantService.tenantsSignal;

  isSuperAdmin = signal<boolean>(false);

  // Modales
  isSuscribirModalOpen = signal<boolean>(false);
  isCambiarModalOpen = signal<boolean>(false);
  isSuspenderModalOpen = signal<boolean>(false);
  selectedSub = signal<Suscripcion | null>(null);

  // Formularios
  formSuscribir = signal<SuscribirEmpresaRequest>({
    idtenant: 0,
    idplan: 0,
    diasvigencia: 30,
    renovacionautomatica: true
  });

  formCambiar = signal<CambiarPlanRequest>({
    idplan: 0,
    diasvigencia: 30,
    renovacionautomatica: true
  });

  motivoSuspension = signal<string>('');

  successMessage = signal<string | null>(null);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    const roles = this.currentUser()?.roles || [];
    const esSuper = roles.includes('SuperAdministrador');
    this.isSuperAdmin.set(esSuper);

    this.subscriptionService.getPlanes(true).subscribe();

    if (esSuper) {
      this.cargarSuscripciones();
      this.tenantService.getTenants('', 0, 100).subscribe();
    } else {
      this.cargarMiSuscripcion();
    }
  }

  cargarSuscripciones(): void {
    this.subscriptionService.getSuscripciones().subscribe({
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cargar suscripciones.');
      }
    });
  }

  cargarMiSuscripcion(): void {
    this.subscriptionService.getMiSuscripcion().subscribe({
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al obtener la suscripción de su empresa.');
      }
    });
  }

  abrirSuscribirModal(): void {
    const planesActivos = this.planes();
    const defaultPlan = planesActivos.length > 0 ? planesActivos[0].idplan : 0;
    const defaultTenant = this.tenants().length > 0 ? this.tenants()[0].idtenant : 0;

    this.formSuscribir.set({
      idtenant: defaultTenant,
      idplan: defaultPlan,
      diasvigencia: 30,
      renovacionautomatica: true
    });
    this.errorMessage.set(null);
    this.isSuscribirModalOpen.set(true);
  }

  abrirCambiarModal(sub: Suscripcion): void {
    this.selectedSub.set(sub);
    const planesActivos = this.planes();
    const defaultPlan = planesActivos.length > 0 ? planesActivos[0].idplan : sub.idplan;

    this.formCambiar.set({
      idplan: defaultPlan,
      diasvigencia: 30,
      renovacionautomatica: sub.renovacionautomatica
    });
    this.errorMessage.set(null);
    this.isCambiarModalOpen.set(true);
  }

  abrirSuspenderModal(sub: Suscripcion): void {
    this.selectedSub.set(sub);
    this.motivoSuspension.set('Incumplimiento de términos o solicitud administrativa');
    this.errorMessage.set(null);
    this.isSuspenderModalOpen.set(true);
  }

  cerrarModales(): void {
    this.isSuscribirModalOpen.set(false);
    this.isCambiarModalOpen.set(false);
    this.isSuspenderModalOpen.set(false);
    this.selectedSub.set(null);
  }

  guardarSuscripcion(): void {
    const payload = this.formSuscribir();
    if (!payload.idtenant || !payload.idplan) {
      this.errorMessage.set('Debe seleccionar empresa y plan.');
      return;
    }

    this.subscriptionService.suscribirEmpresa(payload).subscribe({
      next: () => {
        this.successMessage.set('Empresa suscrita exitosamente al plan.');
        this.cerrarModales();
        this.cargarSuscripciones();
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al suscribir empresa.');
      }
    });
  }

  guardarCambioPlan(): void {
    const sub = this.selectedSub();
    if (!sub) return;

    const payload = this.formCambiar();
    this.subscriptionService.cambiarPlan(sub.idsuscripcion, payload).subscribe({
      next: () => {
        this.successMessage.set('Plan de la empresa actualizado exitosamente.');
        this.cerrarModales();
        if (this.isSuperAdmin()) {
          this.cargarSuscripciones();
        } else {
          this.cargarMiSuscripcion();
        }
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cambiar plan.');
      }
    });
  }

  confirmarSuspension(): void {
    const sub = this.selectedSub();
    if (!sub) return;

    const payload: UpdateSuscripcionEstadoRequest = {
      estado: 'suspendida',
      motivocancelacion: this.motivoSuspension()
    };

    this.subscriptionService.updateEstadoSuscripcion(sub.idsuscripcion, payload).subscribe({
      next: () => {
        this.successMessage.set('Suscripción suspendida.');
        this.cerrarModales();
        this.cargarSuscripciones();
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al suspender suscripción.');
      }
    });
  }

  reactivarSuscripcion(sub: Suscripcion): void {
    const payload: UpdateSuscripcionEstadoRequest = {
      estado: 'activa'
    };

    this.subscriptionService.updateEstadoSuscripcion(sub.idsuscripcion, payload).subscribe({
      next: () => {
        this.successMessage.set('Suscripción reactivada correctamente.');
        this.cargarSuscripciones();
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al reactivar.');
      }
    });
  }
}

