import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { UnitService } from '../services/unit.service';
import { ProductService } from '../services/product.service';
import { ActorService } from '../services/actor.service';
import { LocationService } from '../services/location.service';
import { UnitItem, UnitCreate, Variant, Product } from '../../models/auth.models';

@Component({
  selector: 'app-unit-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/unit-management.view.html',
  styleUrls: ['../../views/pages/unit-management.view.css']
})
export class UnitManagementController implements OnInit {
  private unitService = inject(UnitService);
  private productService = inject(ProductService);
  private actorService = inject(ActorService);
  private locationService = inject(LocationService);

  units = this.unitService.unitsSignal;
  isLoading = this.unitService.loadingSignal;
  total = this.unitService.totalSignal;

  actors = this.actorService.actorsSignal;
  locations = this.locationService.locationsSignal;

  allVariants = signal<Variant[]>([]);

  searchQuery = signal<string>('');
  selectedEstado = signal<string>('');

  isModalOpen = signal<boolean>(false);
  isEditMode = signal<boolean>(false);
  editingId = signal<number | null>(null);

  unitForm: UnitCreate = {
    idvariante: 0,
    numeroserie: '',
    imei1: '',
    imei2: '',
    eid: '',
    idcustodioactual: undefined,
    idubicacionactual: undefined,
    estado: 'disponible'
  };

  estadosUnidad = [
    { value: 'disponible', label: 'Disponible en Stock' },
    { value: 'en_transito', label: 'En Tránsito (Importación/Logística)' },
    { value: 'vendido', label: 'Vendido a Cliente' },
    { value: 'devuelto', label: 'Devuelto por Garantía' },
    { value: 'retirado', label: 'Retirado / De baja' }
  ];

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  Number(val: any): number {
    return Number(val);
  }

  ngOnInit() {
    this.loadUnits();
    this.loadDropdownData();
  }

  loadUnits() {
    this.unitService.getUnits(this.searchQuery(), this.selectedEstado()).subscribe({
      error: (err) => this.errorMessage.set(err?.error?.detail || 'Error cargando unidades.')
    });
  }

  loadDropdownData() {
    this.actorService.getActors('', '', 0, 100).subscribe();
    this.locationService.getLocations('', '', 0, 100).subscribe();

    this.productService.getProducts('', undefined, 0, 100).subscribe({
      next: (res) => {
        const variants: Variant[] = [];
        res.items.forEach((p: Product) => {
          if (p.variantes) {
            p.variantes.forEach((v: Variant) => {
              variants.push({
                ...v,
                sku: `${p.nombre} - ${v.capacidad || ''} ${v.color || ''} (${v.sku})`
              });
            });
          }
        });
        this.allVariants.set(variants);
      }
    });
  }

  onSearch() {
    this.loadUnits();
  }

  openCreateModal() {
    this.isEditMode.set(false);
    this.editingId.set(null);
    const firstVarId = this.allVariants().length > 0 ? this.allVariants()[0].idvariante : 0;
    this.unitForm = {
      idvariante: firstVarId,
      numeroserie: '',
      imei1: '',
      imei2: '',
      eid: '',
      idcustodioactual: undefined,
      idubicacionactual: undefined,
      estado: 'disponible'
    };
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  openEditModal(unit: UnitItem) {
    this.isEditMode.set(true);
    this.editingId.set(unit.idunidad);
    this.unitForm = {
      idvariante: unit.idvariante,
      numeroserie: unit.numeroserie,
      imei1: unit.imei1 || '',
      imei2: unit.imei2 || '',
      eid: unit.eid || '',
      idcustodioactual: unit.idcustodioactual,
      idubicacionactual: unit.idubicacionactual,
      estado: unit.estado || 'disponible'
    };
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  closeModal() {
    this.isModalOpen.set(false);
  }

  saveUnit() {
    if (!this.unitForm.idvariante || !this.unitForm.numeroserie) {
      this.errorMessage.set('Variante de producto y número de serie son obligatorios.');
      return;
    }

    if (this.isEditMode() && this.editingId()) {
      this.unitService.updateUnit(this.editingId()!, this.unitForm).subscribe({
        next: () => {
          this.successMessage.set('Unidad actualizada correctamente.');
          this.closeModal();
          this.loadUnits();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error actualizando unidad.')
      });
    } else {
      this.unitService.createUnit(this.unitForm).subscribe({
        next: () => {
          this.successMessage.set('Unidad de producto registrada con éxito.');
          this.closeModal();
          this.loadUnits();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error registrando unidad.')
      });
    }
  }

  deleteUnit(unit: UnitItem) {
    if (confirm(`¿Está seguro de eliminar la unidad con Serie '${unit.numeroserie}'?`)) {
      this.unitService.deleteUnit(unit.idunidad).subscribe({
        next: () => {
          this.successMessage.set('Unidad eliminada.');
          this.loadUnits();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error eliminando unidad.')
      });
    }
  }
}
