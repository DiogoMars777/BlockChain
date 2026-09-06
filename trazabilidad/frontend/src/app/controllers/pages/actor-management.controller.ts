import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ActorService } from '../services/actor.service';
import { Actor, ActorCreate } from '../../models/auth.models';

@Component({
  selector: 'app-actor-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/actor-management.view.html',
  styleUrls: ['../../views/pages/actor-management.view.css']
})
export class ActorManagementController implements OnInit {
  private actorService = inject(ActorService);

  actors = this.actorService.actorsSignal;
  isLoading = this.actorService.loadingSignal;
  total = this.actorService.totalSignal;

  searchQuery = signal<string>('');
  selectedTipo = signal<string>('');

  isModalOpen = signal<boolean>(false);
  isEditMode = signal<boolean>(false);
  editingId = signal<number | null>(null);

  actorForm: ActorCreate = {
    nombre: '',
    razonsocial: '',
    nit: '',
    email: '',
    telefono: '',
    tipoactor: 'PROVEEDOR_EEUU'
  };

  tiposActor = [
    { value: 'PROVEEDOR_EEUU', label: 'Proveedor EEUU (Apple)' },
    { value: 'TRANSPORTISTA_INTERNACIONAL', label: 'Transportista Internacional (Maersk/FedEx)' },
    { value: 'ADUANA', label: 'Aduana Nacional' },
    { value: 'IMPORTADOR', label: 'Importador Oficial' },
    { value: 'DISTRIBUIDOR', label: 'Distribuidor Mayorista' },
    { value: 'TIENDA', label: 'Tienda Minorista / Reseller' },
    { value: 'CONSUMIDOR', label: 'Cliente Final' }
  ];

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  ngOnInit() {
    this.loadActors();
  }

  loadActors() {
    this.actorService.getActors(this.searchQuery(), this.selectedTipo()).subscribe({
      error: (err) => this.errorMessage.set(err?.error?.detail || 'Error cargando actores.')
    });
  }

  onSearch() {
    this.loadActors();
  }

  openCreateModal() {
    this.isEditMode.set(false);
    this.editingId.set(null);
    this.actorForm = {
      nombre: '',
      razonsocial: '',
      nit: '',
      email: '',
      telefono: '',
      tipoactor: 'PROVEEDOR_EEUU'
    };
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  openEditModal(actor: Actor) {
    this.isEditMode.set(true);
    this.editingId.set(actor.idactor);
    this.actorForm = {
      nombre: actor.nombre,
      razonsocial: actor.razonsocial || '',
      nit: actor.nit || '',
      email: actor.email || '',
      telefono: actor.telefono || '',
      tipoactor: actor.tipoactor
    };
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  closeModal() {
    this.isModalOpen.set(false);
  }

  saveActor() {
    if (!this.actorForm.nombre || !this.actorForm.tipoactor) {
      this.errorMessage.set('Nombre y tipo de actor son obligatorios.');
      return;
    }

    if (this.isEditMode() && this.editingId()) {
      this.actorService.updateActor(this.editingId()!, this.actorForm).subscribe({
        next: () => {
          this.successMessage.set('Actor actualizado correctamente.');
          this.closeModal();
          this.loadActors();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error actualizando actor.')
      });
    } else {
      this.actorService.createActor(this.actorForm).subscribe({
        next: () => {
          this.successMessage.set('Actor registrado correctamente.');
          this.closeModal();
          this.loadActors();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error registrando actor.')
      });
    }
  }

  deleteActor(actor: Actor) {
    if (confirm(`¿Está seguro de eliminar al actor '${actor.nombre}'?`)) {
      this.actorService.deleteActor(actor.idactor).subscribe({
        next: () => {
          this.successMessage.set('Actor eliminado.');
          this.loadActors();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error eliminando actor.')
      });
    }
  }
}
