import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { SubscriptionService } from '../services/subscription.service';
import { AuthService } from '../services/auth.service';
import { Plan, PlanCreate, PlanUpdate } from '../../models/subscription.model';

@Component({
  selector: 'app-subscription-plans',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: '../../views/pages/subscription-plans.view.html',
  styleUrls: ['../../views/pages/subscription-plans.view.css']
})
export class SubscriptionPlansController implements OnInit {
  private subscriptionService = inject(SubscriptionService);
  private authService = inject(AuthService);
  private router = inject(Router);

  planes = this.subscriptionService.planesSignal;
  isLoading = this.subscriptionService.isLoadingSignal;
  currentUser = this.authService.currentUser;

  // Modales y estados
  isModalOpen = signal<boolean>(false);
  isEditing = signal<boolean>(false);
  selectedPlanId = signal<number | null>(null);

  // Formulario
  formPlan = signal<PlanCreate>({
    codigo: '',
    nombre: '',
    descripcion: '',
    preciomensual: 0,
    precioanual: 0,
    moneda: 'USD',
    limiteusuarios: 5,
    limiteunidades: 100,
    limitereportesmes: 200,
    limitealmacenamientomb: 1024,
    diastrial: 14,
    activo: true
  });

  successMessage = signal<string | null>(null);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.cargarPlanes();
  }

  cargarPlanes(): void {
    this.subscriptionService.getPlanes().subscribe({
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cargar los planes.');
      }
    });
  }

  abrirCrearModal(): void {
    this.isEditing.set(false);
    this.selectedPlanId.set(null);
    this.formPlan.set({
      codigo: '',
      nombre: '',
      descripcion: '',
      preciomensual: 29.99,
      precioanual: 299.99,
      moneda: 'USD',
      limiteusuarios: 10,
      limiteunidades: 250,
      limitereportesmes: 500,
      limitealmacenamientomb: 2048,
      diastrial: 14,
      activo: true
    });
    this.errorMessage.set(null);
    this.isModalOpen.set(true);
  }

  abrirEditarModal(plan: Plan): void {
    this.isEditing.set(true);
    this.selectedPlanId.set(plan.idplan);
    this.formPlan.set({
      codigo: plan.codigo,
      nombre: plan.nombre,
      descripcion: plan.descripcion || '',
      preciomensual: Number(plan.preciomensual),
      precioanual: Number(plan.precioanual),
      moneda: plan.moneda,
      limiteusuarios: plan.limiteusuarios,
      limiteunidades: plan.limiteunidades,
      limitereportesmes: plan.limitereportesmes,
      limitealmacenamientomb: plan.limitealmacenamientomb,
      diastrial: plan.diastrial,
      activo: plan.activo
    });
    this.errorMessage.set(null);
    this.isModalOpen.set(true);
  }

  cerrarModal(): void {
    this.isModalOpen.set(false);
  }

  guardarPlan(): void {
    const data = this.formPlan();
    if (!data.nombre || !data.nombre.trim()) {
      this.errorMessage.set('El nombre del plan es obligatorio.');
      return;
    }

    if (this.isEditing()) {
      const planId = this.selectedPlanId();
      if (!planId) return;

      const updateData: PlanUpdate = {
        nombre: data.nombre,
        descripcion: data.descripcion,
        preciomensual: Number(data.preciomensual),
        precioanual: Number(data.precioanual),
        moneda: data.moneda,
        limiteusuarios: Number(data.limiteusuarios),
        limiteunidades: Number(data.limiteunidades),
        limitereportesmes: Number(data.limitereportesmes),
        limitealmacenamientomb: Number(data.limitealmacenamientomb),
        diastrial: Number(data.diastrial),
        activo: data.activo
      };

      this.subscriptionService.updatePlan(planId, updateData).subscribe({
        next: () => {
          this.successMessage.set('Plan actualizado correctamente.');
          this.cerrarModal();
          this.cargarPlanes();
          setTimeout(() => this.successMessage.set(null), 4000);
        },
        error: (err) => {
          this.errorMessage.set(err.error?.detail || 'Error al actualizar el plan.');
        }
      });
    } else {
      if (!data.codigo || !data.codigo.trim()) {
        this.errorMessage.set('El código identificador del plan es obligatorio.');
        return;
      }

      this.subscriptionService.createPlan(data).subscribe({
        next: () => {
          this.successMessage.set('Plan creado con éxito.');
          this.cerrarModal();
          this.cargarPlanes();
          setTimeout(() => this.successMessage.set(null), 4000);
        },
        error: (err) => {
          this.errorMessage.set(err.error?.detail || 'Error al crear el plan.');
        }
      });
    }
  }

  toggleEstado(plan: Plan): void {
    const nuevoEstado = !plan.activo;
    this.subscriptionService.togglePlanEstado(plan.idplan, nuevoEstado).subscribe({
      next: () => {
        this.cargarPlanes();
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cambiar estado.');
      }
    });
  }
}

