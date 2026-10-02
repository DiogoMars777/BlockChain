import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ReceptionService } from '../services/reception.service';
import { PurchaseService } from '../services/purchase.service';
import { LocationService } from '../services/location.service';
import { RecepcionItem, RecepcionDetalle, RecepcionCreate, RecepcionDetalleInput } from '../../models/reception.model';
import { CompraItem } from '../../models/purchase.model';
import { LocationItem } from '../../models/auth.models';

@Component({
  selector: 'app-reception-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/reception-management.view.html',
  styleUrls: ['../../views/pages/reception-management.view.css']
})
export class ReceptionManagementController implements OnInit {
  private receptionService = inject(ReceptionService);
  private purchaseService = inject(PurchaseService);
  private locationService = inject(LocationService);

  recepciones = this.receptionService.recepcionesSignal;
  isLoading = this.receptionService.loadingSignal;
  locations = this.locationService.locationsSignal;

  compras = signal<CompraItem[]>([]);
  selectedEstado = signal<string>('');

  isModalOpen = signal<boolean>(false);
  isSaving = signal<boolean>(false);

  selectedRecepcion = signal<RecepcionDetalle | null>(null);
  isDetailModalOpen = signal<boolean>(false);

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  estadosRecepcion = [
    { value: '', label: '-- Todos los Estados --' },
    { value: 'pendiente', label: 'Pendiente' },
    { value: 'parcial', label: 'Parcial' },
    { value: 'completa', label: 'Completa' },
    { value: 'rechazada', label: 'Rechazada' }
  ];

  receptionForm: RecepcionCreate = {
    idcompra: 0,
    idubicacion: 0,
    numerodocumento: '',
    estado: 'pendiente',
    detalles: []
  };

  ngOnInit(): void {
    this.loadRecepciones();
    this.loadDropdownData();
  }

  loadRecepciones(): void {
    this.errorMessage.set('');
    this.receptionService.getRecepciones(this.selectedEstado()).subscribe({
      error: (err) => this.errorMessage.set(err?.error?.detail || 'Error al cargar las recepciones.')
    });
  }

  loadDropdownData(): void {
    this.locationService.getLocations('', '', 0, 100).subscribe();
    this.purchaseService.getPurchases('', 0, 100).subscribe({
      next: (res) => this.compras.set(res.items),
      error: () => this.compras.set([])
    });
  }

  /** Solo las ordenes que aun admiten recepciones: no finalizadas ni anuladas. */
  comprasRecepcionables(): CompraItem[] {
    return this.compras().filter(c => ['enviada', 'recibida_parcial'].includes((c.estado || '').toLowerCase()));
  }

  selectedCompra(): CompraItem | null {
    return this.compras().find(c => c.idcompra === this.receptionForm.idcompra) || null;
  }

  etiquetaEstado(estado: string): string {
    const f = this.estadosRecepcion.find(e => e.value === estado?.toLowerCase());
    return f && f.value ? f.label : estado;
  }

  getEstadoClass(estado: string): string {
    switch ((estado || '').toLowerCase()) {
      case 'pendiente': return 'pendiente';
      case 'parcial': return 'parcial';
      case 'completa': return 'completa';
      case 'rechazada': return 'rechazada';
      default: return 'pendiente';
    }
  }

  formatDate(value?: string): string {
    if (!value) return 'N/A';
    const d = new Date(value);
    return isNaN(d.getTime()) ? value : d.toLocaleString('es-BO');
  }

  // ---------- Registro de recepcion (CU-012) ----------

  openCreateModal(): void {
    const compras = this.comprasRecepcionables();
    const primera = compras.length > 0 ? compras[0] : null;
    const primeraLoc = this.locations()[0]?.idubicacion || 0;

    this.receptionForm = {
      idcompra: primera ? primera.idcompra : 0,
      idubicacion: primeraLoc,
      numerodocumento: '',
      estado: 'pendiente',
      detalles: this.detallesDesdeCompra(primera)
    };
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  /** Precarga las lineas del formulario con lo pedido en la orden de compra. */
  detallesDesdeCompra(compra: CompraItem | null): RecepcionDetalleInput[] {
    if (!compra || !compra.detalles) return [];
    return compra.detalles.map(d => ({
      idvariante: d.idvariante,
      cantidadesperada: d.cantidad,
      cantidadrecibida: d.cantidad
    }));
  }

  onCompraChange(idcompra: number): void {
    this.receptionForm.idcompra = Number(idcompra);
    this.receptionForm.detalles = this.detallesDesdeCompra(this.selectedCompra());
  }

  /** Agrega una linea en blanco cuando el usuario no alcanzo a Receptionar todo. */
  addDetalle(): void {
    this.receptionForm.detalles.push({ idvariante: 0, cantidadesperada: 1, cantidadrecibida: 0 });
  }

  removeDetalle(index: number): void {
    this.receptionForm.detalles.splice(index, 1);
  }

  private validate(): string | null {
    if (!this.receptionForm.idcompra) return 'Debe seleccionar la orden de compra que se está recibiendo.';
    if (!this.receptionForm.idubicacion) return 'Debe seleccionar la ubicación física de recepción.';
    if (!this.receptionForm.numerodocumento.trim()) return 'Debe ingresar el número de documento de recepción.';

    const detalles = this.receptionForm.detalles.filter(d => d.idvariante);
    if (detalles.length === 0) return 'Debe registrar al menos un producto recibido.';
    if (detalles.some(d => d.cantidadesperada < 1)) return 'La cantidad esperada debe ser mayor que cero.';
    if (detalles.some(d => d.cantidadrecibida < 0)) return 'La cantidad recibida no puede ser negativa.';
    if (detalles.some(d => d.cantidadrecibida > d.cantidadesperada)) {
      return 'La cantidad recibida no puede superar la cantidad esperada.';
    }
    return null;
  }

  saveRecepcion(): void {
    const error = this.validate();
    if (error) {
      this.errorMessage.set(error);
      return;
    }

    this.errorMessage.set('');
    this.isSaving.set(true);

    const payload: RecepcionCreate = {
      ...this.receptionForm,
      numerodocumento: this.receptionForm.numerodocumento.trim(),
      detalles: this.receptionForm.detalles.filter(d => d.idvariante)
    };

    this.receptionService.createRecepcion(payload).subscribe({
      next: (res) => {
        this.isSaving.set(false);
        this.isModalOpen.set(false);
        this.successMessage.set(res.message);
        this.loadRecepciones();
        this.loadDropdownData();
        setTimeout(() => this.successMessage.set(''), 6000);
      },
      error: (err) => {
        this.isSaving.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al registrar la recepción.');
      }
    });
  }

  // ---------- Detalle y cierre de recepcion ----------

  openDetail(recepcion: RecepcionItem): void {
    this.selectedRecepcion.set(null);
    this.isDetailModalOpen.set(true);
    this.errorMessage.set('');
    this.receptionService.getRecepcion(recepcion.idrecepcion).subscribe({
      next: (res) => this.selectedRecepcion.set(res),
      error: (err) => {
        this.isDetailModalOpen.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al cargar el detalle de la recepción.');
      }
    });
  }

  closeDetail(): void {
    this.isDetailModalOpen.set(false);
    this.selectedRecepcion.set(null);
  }

  transicionesDisponibles(estado: string): string[] {
    const mapa: Record<string, string[]> = {
      pendiente: ['parcial', 'completa', 'rechazada'],
      parcial: ['parcial', 'completa', 'rechazada'],
      completa: [],
      rechazada: []
    };
    return mapa[(estado || '').toLowerCase()] ?? [];
  }

  cambiarEstado(recepcion: RecepcionItem, nuevo: string): void {
    this.errorMessage.set('');
    this.receptionService.updateEstado(recepcion.idrecepcion, nuevo).subscribe({
      next: (res) => {
        this.successMessage.set(res.message);
        this.selectedRecepcion.set(res.recepcion);
        this.loadRecepciones();
        this.loadDropdownData();
        setTimeout(() => this.successMessage.set(''), 6000);
      },
      error: (err) => this.errorMessage.set(err?.error?.detail || 'Error al cambiar el estado de la recepción.')
    });
  }
}
