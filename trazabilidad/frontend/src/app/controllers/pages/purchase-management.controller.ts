import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { PurchaseService } from '../services/purchase.service';
import { ActorService } from '../services/actor.service';
import { TenantCatalogService } from '../services/tenant-catalog.service';
import { CompraItem, CompraDetalleCreate, CompraCreate } from '../../models/purchase.model';
import { Actor } from '../../models/auth.models';
import { TenantCatalogItem } from '../../models/auth.models';

@Component({
  selector: 'app-purchase-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/purchase-management.view.html',
  styleUrls: ['../../views/pages/purchase-management.view.css']
})
export class PurchaseManagementController implements OnInit {
  private purchaseService = inject(PurchaseService);
  private actorService = inject(ActorService);
  private catalogService = inject(TenantCatalogService);

  purchases = this.purchaseService.purchasesSignal;
  total = this.purchaseService.totalSignal;
  isLoading = this.purchaseService.loadingSignal;

  selectedEstado = signal<string>('');
  selectedPurchase = signal<CompraItem | null>(null);

  isDetailModalOpen = signal<boolean>(false);
  isApproveModalOpen = signal<boolean>(false);
  isRejectModalOpen = signal<boolean>(false);

  // --- Formulario de alta / edicion (CU-010) ---
  isFormModalOpen = signal<boolean>(false);
  isEditMode = signal<boolean>(false);
  editingId = signal<number | null>(null);
  isSaving = signal<boolean>(false);

  proveedores = signal<Actor[]>([]);
  catalogo = signal<TenantCatalogItem[]>([]);

  compraForm: CompraCreate = {
    idproveedor: 0,
    numeroorden: '',
    fechacompra: '',
    detalles: []
  };

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
    this.loadFormData();
  }

  /**
   * Carga los datos que alimentan los selectores del formulario: los actores que
   * pueden actuar como proveedor y las variantes del catalogo de la empresa.
   */
  loadFormData(): void {
    this.actorService.getActors('', 'PROVEEDOR_EEUU', 0, 100).subscribe({
      next: (res) => this.proveedores.set(res.items),
      error: () => this.proveedores.set([])
    });

    this.catalogService.getCatalog('', undefined, 0, 100).subscribe({
      next: (res) => this.catalogo.set(res.items.filter(c => c.activo)),
      error: () => this.catalogo.set([])
    });
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

  // ---------- Formulario de alta / edicion ----------

  private todayISO(): string {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  }

  openCreateModal(): void {
    this.isEditMode.set(false);
    this.editingId.set(null);
    this.compraForm = {
      idproveedor: 0,
      numeroorden: '',
      fechacompra: this.todayISO(),
      detalles: []
    };
    this.errorMessage.set('');
    this.isFormModalOpen.set(true);
  }

  openEditModal(compra: CompraItem): void {
    this.isEditMode.set(true);
    this.editingId.set(compra.idcompra);
    this.compraForm = {
      idproveedor: compra.idproveedor,
      numeroorden: compra.numeroorden,
      fechacompra: compra.fechacompra,
      detalles: (compra.detalles ?? []).map(d => ({
        idvariante: d.idvariante,
        cantidad: d.cantidad,
        costounitariousd: Number(d.costounitariousd)
      }))
    };
    this.errorMessage.set('');
    this.isFormModalOpen.set(true);
  }

  closeForm(): void {
    this.isFormModalOpen.set(false);
    this.isSaving.set(false);
  }

  addDetalle(): void {
    this.compraForm.detalles = [...this.compraForm.detalles, { idvariante: 0, cantidad: 1, costounitariousd: 0 }];
  }

  removeDetalle(index: number): void {
    this.compraForm.detalles = this.compraForm.detalles.filter((_, i) => i !== index);
  }

  /** Etiqueta legible de una variante del catalogo: SKU + color. */
  varianteLabel(c: TenantCatalogItem): string {
    const sku = c.variante?.sku ?? `#${c.idvariante}`;
    const color = c.variante?.color;
    return color ? `${sku} (${color})` : sku;
  }

  isDetalleValido(d: CompraDetalleCreate): boolean {
    return d.idvariante > 0 && d.cantidad > 0 && d.costounitariousd > 0;
  }

  subtotal(d: CompraDetalleCreate): number {
    return d.cantidad * d.costounitariousd;
  }

  formTotal(): number {
    return this.compraForm.detalles.reduce((acc, d) => acc + this.subtotal(d), 0);
  }

  private validateForm(): string | null {
    if (!this.compraForm.idproveedor) return 'Debe seleccionar un proveedor.';
    if (!this.compraForm.numeroorden.trim()) return 'Debe ingresar el número de orden.';
    if (!this.compraForm.fechacompra) return 'Debe seleccionar la fecha de compra.';
    if (this.compraForm.detalles.length === 0) return 'Debe agregar al menos una línea de detalle.';

    for (const d of this.compraForm.detalles) {
      if (!d.idvariante) return 'Todas las líneas deben tener una variante seleccionada.';
      if (d.cantidad <= 0) return 'La cantidad debe ser mayor a 0.';
      if (d.costounitariousd <= 0) return 'El costo unitario debe ser mayor a 0.';
    }

    const repetidas = this.compraForm.detalles
      .map(d => d.idvariante)
      .filter((id, i, arr) => arr.indexOf(id) !== i);
    if (repetidas.length) return 'No se puede repetir la misma variante en dos líneas.';

    return null;
  }

  saveCompra(): void {
    const error = this.validateForm();
    if (error) {
      this.errorMessage.set(error);
      return;
    }

    this.errorMessage.set('');
    this.isSaving.set(true);

    const payload = {
      idproveedor: Number(this.compraForm.idproveedor),
      numeroorden: this.compraForm.numeroorden.trim(),
      fechacompra: this.compraForm.fechacompra,
      detalles: this.compraForm.detalles.map(d => ({
        idvariante: Number(d.idvariante),
        cantidad: Number(d.cantidad),
        costounitariousd: Number(d.costounitariousd)
      }))
    };

    const esEdicion = this.isEditMode() && this.editingId() !== null;
    const request$ = esEdicion
      ? this.purchaseService.updatePurchase(this.editingId()!, payload)
      : this.purchaseService.createPurchase(payload);

    request$.subscribe({
      next: () => {
        this.isSaving.set(false);
        this.closeForm();
        this.closeDetail();
        this.successMessage.set(
          esEdicion
            ? `Orden de compra #${payload.numeroorden} actualizada correctamente.`
            : `Orden de compra #${payload.numeroorden} creada correctamente.`
        );
        this.loadPurchases();
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => {
        this.isSaving.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al guardar la orden de compra.');
      }
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
