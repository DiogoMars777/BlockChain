import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { PurchaseService } from '../services/purchase.service';
import { CompraItem, CompraDetalleItem } from '../../models/purchase.model';

@Component({
  selector: 'app-purchase-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/purchase-management.view.html',
  styleUrls: ['../../views/pages/purchase-management.view.css']
})
export class PurchaseManagementController implements OnInit {
  private purchaseService = inject(PurchaseService);

  purchases = this.purchaseService.purchasesSignal;
  total = this.purchaseService.totalSignal;
  isLoading = this.purchaseService.loadingSignal;

  selectedEstado = signal<string>('');
  selectedPurchase = signal<CompraItem | null>(null);

  isDetailModalOpen = signal<boolean>(false);
  isApproveModalOpen = signal<boolean>(false);
  isRejectModalOpen = signal<boolean>(false);

  rejectReason = signal<string>('');

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  estadosFiltro = [
    { value: '', label: '-- Todos los estados --' },
    { value: 'pendiente', label: 'Pendiente de Aprobación' },
    { value: 'enviada', label: 'Aprobada / Enviada' },
    { value: 'recibida_total', label: 'Recibida en Almacén' },
    { value: 'cancelada', label: 'Rechazada / Cancelada' }
  ];

  ngOnInit(): void {
    this.loadPurchases();
  }

  loadPurchases(): void {
    this.errorMessage.set('');
    this.purchaseService.getPurchases(this.selectedEstado()).subscribe({
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al cargar las compras.')
    });
  }

  onFilterChange(): void {
    this.loadPurchases();
  }

  openDetail(compra: CompraItem): void {
    this.selectedPurchase.set(compra);
    this.isDetailModalOpen.set(true);
  }

  closeDetail(): void {
    this.isDetailModalOpen.set(false);
  }

  openApprove(compra: CompraItem): void {
    this.selectedPurchase.set(compra);
    this.isApproveModalOpen.set(true);
  }

  closeApprove(): void {
    this.isApproveModalOpen.set(false);
  }

  confirmApprove(): void {
    const p = this.selectedPurchase();
    if (!p) return;

    this.errorMessage.set('');
    this.purchaseService.approvePurchase(p.idcompra).subscribe({
      next: (res) => {
        this.successMessage.set(res.message);
        this.closeApprove();
        this.closeDetail();
        this.loadPurchases();
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al aprobar la compra.')
    });
  }

  openReject(compra: CompraItem): void {
    this.selectedPurchase.set(compra);
    this.rejectReason.set('');
    this.isRejectModalOpen.set(true);
  }

  closeReject(): void {
    this.isRejectModalOpen.set(false);
  }

  confirmReject(): void {
    const p = this.selectedPurchase();
    const motivo = this.rejectReason().trim();

    if (!p) return;
    if (motivo.length < 5) {
      this.errorMessage.set('Debe ingresar un motivo justificado de al menos 5 caracteres.');
      return;
    }

    this.errorMessage.set('');
    this.purchaseService.rejectPurchase(p.idcompra, motivo).subscribe({
      next: (res) => {
        this.successMessage.set(res.message);
        this.closeReject();
        this.closeDetail();
        this.loadPurchases();
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al rechazar la compra.')
    });
  }

  getEstadoClass(estado: string): string {
    switch (estado.toLowerCase()) {
      case 'pendiente': return 'badge-warning';
      case 'enviada': return 'badge-info';
      case 'recibida_total': return 'badge-success';
      case 'cancelada': return 'badge-danger';
      default: return 'badge-secondary';
    }
  }

  getEstadoLabel(estado: string): string {
    switch (estado.toLowerCase()) {
      case 'pendiente': return 'Pendiente';
      case 'enviada': return 'Aprobada / Enviada';
      case 'recibida_total': return 'Recibida';
      case 'cancelada': return 'Rechazada';
      default: return estado;
    }
  }
}
