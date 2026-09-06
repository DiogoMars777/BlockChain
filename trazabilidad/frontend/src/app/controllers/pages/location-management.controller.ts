import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LocationService } from '../services/location.service';
import { ActorService } from '../services/actor.service';
import { LocationItem, LocationCreate } from '../../models/auth.models';

@Component({
  selector: 'app-location-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/location-management.view.html',
  styleUrls: ['../../views/pages/location-management.view.css']
})
export class LocationManagementController implements OnInit {
  private locationService = inject(LocationService);
  private actorService = inject(ActorService);

  locations = this.locationService.locationsSignal;
  isLoading = this.locationService.loadingSignal;
  total = this.locationService.totalSignal;

  actors = this.actorService.actorsSignal;

  searchQuery = signal<string>('');
  selectedTipo = signal<string>('');

  isModalOpen = signal<boolean>(false);
  isEditMode = signal<boolean>(false);
  editingId = signal<number | null>(null);

  locationForm: LocationCreate = {
    nombre: '',
    idactor: undefined,
    direccion: '',
    ciudad: '',
    pais: '',
    tipo: 'almacen'
  };

  tiposUbicacion = [
    { value: 'origen', label: 'Origen (Fábrica / Cupertino)' },
    { value: 'almacen', label: 'Almacén Principal' },
    { value: 'centro_distribucion', label: 'Centro de Distribución' },
    { value: 'punto_venta', label: 'Punto de Venta / Tienda' },
    { value: 'puerto', label: 'Puerto Marítimo / Aéreo' },
    { value: 'aduana', label: 'Aduana Nacional' }
  ];

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  Number(val: any): number {
    return Number(val);
  }

  ngOnInit() {
    this.loadLocations();
    this.actorService.getActors('', '', 0, 100).subscribe();
  }

  loadLocations() {
    this.locationService.getLocations(this.searchQuery(), this.selectedTipo()).subscribe({
      error: (err) => this.errorMessage.set(err?.error?.detail || 'Error cargando ubicaciones.')
    });
  }

  onSearch() {
    this.loadLocations();
  }

  openCreateModal() {
    this.isEditMode.set(false);
    this.editingId.set(null);
    this.locationForm = {
      nombre: '',
      idactor: undefined,
      direccion: '',
      ciudad: '',
      pais: '',
      tipo: 'almacen'
    };
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  openEditModal(loc: LocationItem) {
    this.isEditMode.set(true);
    this.editingId.set(loc.idubicacion);
    this.locationForm = {
      nombre: loc.nombre,
      idactor: loc.idactor,
      direccion: loc.direccion || '',
      ciudad: loc.ciudad || '',
      pais: loc.pais || '',
      tipo: loc.tipo
    };
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  closeModal() {
    this.isModalOpen.set(false);
  }

  saveLocation() {
    if (!this.locationForm.nombre || !this.locationForm.tipo) {
      this.errorMessage.set('Nombre y tipo de ubicación son obligatorios.');
      return;
    }

    if (this.isEditMode() && this.editingId()) {
      this.locationService.updateLocation(this.editingId()!, this.locationForm).subscribe({
        next: () => {
          this.successMessage.set('Ubicación actualizada correctamente.');
          this.closeModal();
          this.loadLocations();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error actualizando ubicación.')
      });
    } else {
      this.locationService.createLocation(this.locationForm).subscribe({
        next: () => {
          this.successMessage.set('Ubicación registrada correctamente.');
          this.closeModal();
          this.loadLocations();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error registrando ubicación.')
      });
    }
  }

  deleteLocation(loc: LocationItem) {
    if (confirm(`¿Está seguro de eliminar la ubicación '${loc.nombre}'?`)) {
      this.locationService.deleteLocation(loc.idubicacion).subscribe({
        next: () => {
          this.successMessage.set('Ubicación eliminada.');
          this.loadLocations();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error eliminando ubicación.')
      });
    }
  }
}
