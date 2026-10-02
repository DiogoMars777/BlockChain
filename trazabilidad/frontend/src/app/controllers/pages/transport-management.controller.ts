import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TransportService } from '../services/transport.service';
import { LocationService } from '../services/location.service';
import { ActorService } from '../services/actor.service';
import { EnvioItem, EnvioTimelineResponse, CreateTransportEventPayload, EnvioCreate, EnvioDetalle, EnvioUnidadesResponse, EnvioUnidadCandidateItem } from '../../models/transport.model';
import { LocationItem, Actor } from '../../models/auth.models';

@Component({
  selector: 'app-transport-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/transport-management.view.html',
  styleUrls: ['../../views/pages/transport-management.view.css']
})
export class TransportManagementController implements OnInit {
  private transportService = inject(TransportService);
  private locationService = inject(LocationService);
  private actorService = inject(ActorService);

  shipments = this.transportService.shipmentsSignal;
  isLoading = this.transportService.loadingSignal;
  locations = this.locationService.locationsSignal;

  selectedEstado = signal<string>('');
  selectedShipment = signal<EnvioItem | null>(null);
  timelineData = signal<EnvioTimelineResponse | null>(null);

  isTimelineModalOpen = signal<boolean>(false);
  isRecordModalOpen = signal<boolean>(false);

  // --- Asignacion / desasignacion de unidades al envio (CU-020) ---
  isUnitsModalOpen = signal<boolean>(false);
  unitsData = signal<EnvioUnidadesResponse | null>(null);
  isLoadingUnits = signal<boolean>(false);
  unitSearch = signal<string>('');
  selectedCandidateId = signal<number | null>(null);
  isMutatingUnits = signal<boolean>(false);

  // --- Formulario de alta / edicion de envio (CU-019) ---
  isFormModalOpen = signal<boolean>(false);
  isEditMode = signal<boolean>(false);
  editingId = signal<number | null>(null);
  isSaving = signal<boolean>(false);

  actores = signal<Actor[]>([]);
  origenes = signal<Actor[]>([]);
  destinos = signal<Actor[]>([]);
  transportistas = signal<Actor[]>([]);

  envioForm: EnvioCreate = {
    idactororigen: 0,
    idactordestino: 0,
    idtransportista: undefined,
    codigoenvio: '',
    fechaestimada: '',
    trackingexterno: ''
  };

  /** Indica que el usuario eligio explicitamente "sin transportista" en una edicion. */
  clearTransportista = false;

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  // Formulario de nuevo evento
  newEventForm: CreateTransportEventPayload = {
    tipoevento: 'transporte_terrestre',
    idubicacion: 0,
    descripcion: '',
    condiciones: {
      temperatura: undefined,
      humedad: undefined,
      presion: undefined,
      nivelvibracion: undefined,
      fuentedatos: 'Plataforma Web Control'
    }
  };

  tiposEvento = [
    { value: 'transporte_terrestre', label: '🚚 Transporte Terrestre', icon: '🚚' },
    { value: 'transporte_aereo', label: '✈️ Transporte Aéreo', icon: '✈️' },
    { value: 'transporte_maritimo', label: '🚢 Transporte Marítimo', icon: '🚢' },
    { value: 'llegada_puerto', label: '⚓ Llegada a Puerto', icon: '⚓' },
    { value: 'despacho_aduanero', label: '🏢 Despacho Aduanero', icon: '🏢' },
    { value: 'recepcion_almacen', label: '📦 Recepción en Almacén', icon: '📦' }
  ];

  estadosEnvio = [
    { value: '', label: '-- Todos los estados --' },
    { value: 'preparacion', label: 'En Preparación' },
    { value: 'en_transito', label: 'En Tránsito' },
    { value: 'entregado', label: 'Entregado' },
    { value: 'retrasado', label: 'Retrasado' },
    { value: 'cancelado', label: 'Cancelado' }
  ];

  ngOnInit(): void {
    this.loadShipments();
    this.locationService.getLocations().subscribe();
    this.loadActores();
  }

  /** Carga los actores y los clasifica segun el rol que pueden jugar en un envio. */
  loadActores(): void {
    this.actorService.getActors('', '', 0, 100).subscribe({
      next: (res) => {
        const todos = res.items;
        this.actores.set(todos);
        this.origenes.set(todos.filter(a => ['PROVEEDOR_EEUU', 'IMPORTADOR', 'DISTRIBUIDOR'].includes(a.tipoactor)));
        this.destinos.set(todos.filter(a => ['DISTRIBUIDOR', 'TIENDA', 'CONSUMIDOR'].includes(a.tipoactor)));
        this.transportistas.set(todos.filter(a => a.tipoactor === 'TRANSPORTISTA_INTERNACIONAL'));
      },
      error: () => this.actores.set([])
    });
  }

  loadShipments(): void {
    this.errorMessage.set('');
    this.transportService.getShipments(this.selectedEstado()).subscribe({
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al cargar envíos.')
    });
  }

  openTimeline(shipment: EnvioItem): void {
    this.selectedShipment.set(shipment);
    this.isTimelineModalOpen.set(true);
    this.loadTimeline(shipment.idenvio);
  }

  loadTimeline(idenvio: number): void {
    this.transportService.getTimeline(idenvio).subscribe({
      next: (res) => this.timelineData.set(res),
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al cargar la línea de tiempo.')
    });
  }

  closeTimeline(): void {
    this.isTimelineModalOpen.set(false);
    this.timelineData.set(null);
  }

  openRecordModal(shipment: EnvioItem): void {
    this.selectedShipment.set(shipment);
    const firstLoc = this.locations()[0]?.idubicacion || 0;
    this.newEventForm = {
      tipoevento: 'transporte_terrestre',
      idubicacion: firstLoc,
      descripcion: '',
      condiciones: {
        temperatura: 21.0,
        humedad: 45.0,
        presion: 1013.25,
        nivelvibracion: 0.1,
        fuentedatos: 'Plataforma Web Control'
      }
    };
    this.isRecordModalOpen.set(true);
  }

  closeRecordModal(): void {
    this.isRecordModalOpen.set(false);
  }

  saveEvent(): void {
    const s = this.selectedShipment();
    if (!s) return;

    if (!this.newEventForm.idubicacion) {
      this.errorMessage.set('Debe seleccionar una ubicación física.');
      return;
    }

    this.errorMessage.set('');
    this.transportService.recordEvent(s.idenvio, this.newEventForm).subscribe({
      next: () => {
        this.successMessage.set('Evento de trazabilidad y condiciones registradas exitosamente.');
        this.closeRecordModal();
        this.loadShipments();
        if (this.isTimelineModalOpen()) {
          this.loadTimeline(s.idenvio);
        }
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al registrar evento.')
    });
  }

  // ---------- Formulario de alta / edicion de envio (CU-019) ----------

  actorLabel(a: Actor): string {
    return a.razonsocial || a.nombre;
  }

  /** Transiciones que el backend acepta desde el estado actual. */
  transicionesDisponibles(estado: string): string[] {
    const mapa: Record<string, string[]> = {
      preparacion: ['en_transito', 'cancelado'],
      en_transito: ['entregado', 'retrasado', 'cancelado'],
      retrasado: ['en_transito', 'entregado', 'cancelado'],
      entregado: [],
      cancelado: []
    };
    return mapa[estado?.toLowerCase()] ?? [];
  }

  etiquetaEstado(estado: string): string {
    const f = this.estadosEnvio.find(e => e.value === estado?.toLowerCase());
    return f ? f.label.replace('-- ', '').replace(' --', '') : estado;
  }

  openCreateModal(): void {
    this.isEditMode.set(false);
    this.editingId.set(null);
    this.clearTransportista = false;
    this.envioForm = {
      idactororigen: 0,
      idactordestino: 0,
      idtransportista: undefined,
      codigoenvio: '',
      fechaestimada: '',
      trackingexterno: ''
    };
    this.errorMessage.set('');
    this.isFormModalOpen.set(true);
  }

  openEditModal(shipment: EnvioItem): void {
    this.isEditMode.set(true);
    this.editingId.set(shipment.idenvio);
    this.clearTransportista = !shipment.idtransportista;
    this.envioForm = {
      idactororigen: shipment.idactororigen,
      idactordestino: shipment.idactordestino,
      idtransportista: shipment.idtransportista,
      codigoenvio: shipment.codigoenvio,
      fechaestimada: shipment.fechaestimada ? shipment.fechaestimada.slice(0, 16) : '',
      trackingexterno: shipment.trackingexterno || ''
    };
    this.errorMessage.set('');
    this.isFormModalOpen.set(true);
  }

  closeForm(): void {
    this.isFormModalOpen.set(false);
    this.isSaving.set(false);
  }

  onTransportistaChange(val: any): void {
    this.clearTransportista = !val;
    if (val) {
      this.envioForm.idtransportista = Number(val);
    } else {
      this.envioForm.idtransportista = undefined;
    }
  }

  private validateEnvioForm(): string | null {
    if (!this.isEditMode() && !this.envioForm.codigoenvio.trim()) return 'Debe ingresar el código de envío.';
    if (this.isEditMode()) return null;
    if (!this.envioForm.idactororigen) return 'Debe seleccionar el actor de origen.';
    if (!this.envioForm.idactordestino) return 'Debe seleccionar el actor de destino.';
    if (this.envioForm.idactororigen === this.envioForm.idactordestino) {
      return 'El actor de origen y el de destino no pueden ser el mismo.';
    }
    return null;
  }

  saveEnvio(): void {
    const error = this.validateEnvioForm();
    if (error) {
      this.errorMessage.set(error);
      return;
    }

    this.errorMessage.set('');
    this.isSaving.set(true);

    const esEdicion = this.isEditMode() && this.editingId() !== null;
    let request$;

    if (esEdicion) {
      const payload: any = {};
      if (this.envioForm.idactordestino) payload.idactordestino = Number(this.envioForm.idactordestino);
      if (this.envioForm.fechaestimada) payload.fechaestimada = new Date(this.envioForm.fechaestimada).toISOString();
      if (this.clearTransportista) {
        payload.idtransportista = null;
      } else if (this.envioForm.idtransportista) {
        payload.idtransportista = Number(this.envioForm.idtransportista);
      }
      payload.trackingexterno = this.envioForm.trackingexterno || null;
      request$ = this.transportService.updateShipment(this.editingId()!, payload);
    } else {
      const payload: EnvioCreate = {
        idactororigen: Number(this.envioForm.idactororigen),
        idactordestino: Number(this.envioForm.idactordestino),
        codigoenvio: this.envioForm.codigoenvio.trim(),
        fechaestimada: this.envioForm.fechaestimada
          ? new Date(this.envioForm.fechaestimada).toISOString()
          : undefined,
        trackingexterno: this.envioForm.trackingexterno || undefined
      };
      if (this.envioForm.idtransportista) {
        payload.idtransportista = Number(this.envioForm.idtransportista);
      }
      request$ = this.transportService.createShipment(payload);
    }

    request$.subscribe({
      next: (res) => {
        this.isSaving.set(false);
        this.closeForm();
        this.successMessage.set(
          esEdicion
            ? `Envío ${res.codigoenvio} actualizado correctamente.`
            : `Envío ${res.codigoenvio} registrado correctamente.`
        );
        this.loadShipments();
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => {
        this.isSaving.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al guardar el envío.');
      }
    });
  }

  cambiarEstado(shipment: EnvioItem, nuevo: string): void {
    this.errorMessage.set('');
    this.transportService.updateEstado(shipment.idenvio, nuevo).subscribe({
      next: (res) => {
        this.successMessage.set(`Envío ${res.codigoenvio}: estado actualizado a ${this.etiquetaEstado(nuevo)}.`);
        this.loadShipments();
        if (this.selectedShipment()?.idenvio === shipment.idenvio) {
          this.selectedShipment.set(res);
          this.loadTimeline(shipment.idenvio);
        }
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al cambiar el estado del envío.')
    });
  }

  // ---------- Asignacion / desasignacion de unidades al envio (CU-020) ----------

  /** Solo en preparacion el contenido del envio es mutable. */
  puedeEditarUnidades(shipment: EnvioItem): boolean {
    return (shipment.estado || '').toLowerCase() === 'preparacion';
  }

  openUnitsModal(shipment: EnvioItem): void {
    this.selectedShipment.set(shipment);
    this.unitSearch.set('');
    this.selectedCandidateId.set(null);
    this.isUnitsModalOpen.set(true);
    this.loadShipmentUnits(shipment.idenvio);
  }

  closeUnitsModal(): void {
    this.isUnitsModalOpen.set(false);
    this.unitsData.set(null);
    this.selectedCandidateId.set(null);
  }

  loadShipmentUnits(idenvio: number): void {
    this.isLoadingUnits.set(true);
    this.transportService.getShipmentUnits(idenvio).subscribe({
      next: (res) => {
        this.unitsData.set(res);
        this.isLoadingUnits.set(false);
      },
      error: (err) => {
        this.isLoadingUnits.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al cargar las unidades del envío.');
      }
    });
  }

  /** Candidatas filtradas por el texto de busqueda del modal. */
  candidatasFiltradas(): EnvioUnidadCandidateItem[] {
    const disponibles = this.unitsData()?.disponibles ?? [];
    const term = this.unitSearch().trim().toLowerCase();
    if (!term) return disponibles;
    return disponibles.filter(c =>
      c.numeroserie.toLowerCase().includes(term) ||
      (c.sku || '').toLowerCase().includes(term) ||
      (c.producto_nombre || '').toLowerCase().includes(term)
    );
  }

  selectCandidate(candidate: EnvioUnidadCandidateItem): void {
    this.selectedCandidateId.set(
      this.selectedCandidateId() === candidate.idunidad ? null : candidate.idunidad
    );
  }

  candidateLabel(candidate: EnvioUnidadCandidateItem): string {
    return `${candidate.numeroserie} — ${candidate.sku || 'Sin SKU'} (${candidate.producto_nombre || ''})`;
  }

  assignSelectedUnit(): void {
    const s = this.selectedShipment();
    const idunidad = this.selectedCandidateId();
    if (!s || idunidad === null) return;

    this.errorMessage.set('');
    this.isMutatingUnits.set(true);
    this.transportService.assignUnit(s.idenvio, idunidad).subscribe({
      next: (res) => {
        this.isMutatingUnits.set(false);
        this.successMessage.set(res.message);
        this.selectedCandidateId.set(null);
        this.loadShipmentUnits(s.idenvio);
        this.loadShipments();
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => {
        this.isMutatingUnits.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al asignar la unidad al envío.');
      }
    });
  }

  assignAllFiltered(): void {
    const s = this.selectedShipment();
    const ids = this.candidatasFiltradas().map(c => c.idunidad);
    if (!s || ids.length === 0) return;

    this.errorMessage.set('');
    this.isMutatingUnits.set(true);
    this.transportService.assignUnitsBulk(s.idenvio, ids).subscribe({
      next: (res) => {
        this.isMutatingUnits.set(false);
        this.successMessage.set(res.message);
        this.loadShipmentUnits(s.idenvio);
        this.loadShipments();
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => {
        this.isMutatingUnits.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al asignar las unidades al envío.');
      }
    });
  }

  unassignUnit(idunidad: number, numeroserie: string): void {
    const s = this.selectedShipment();
    if (!s) return;
    if (!confirm(`¿Desasignar la unidad '${numeroserie}' del envío ${s.codigoenvio}?`)) return;

    this.errorMessage.set('');
    this.isMutatingUnits.set(true);
    this.transportService.unassignUnit(s.idenvio, idunidad).subscribe({
      next: (res) => {
        this.isMutatingUnits.set(false);
        this.successMessage.set(res.message);
        this.loadShipmentUnits(s.idenvio);
        this.loadShipments();
        setTimeout(() => this.successMessage.set(''), 5000);
      },
      error: (err) => {
        this.isMutatingUnits.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al desasignar la unidad del envío.');
      }
    });
  }

  getEstadoClass(estado: string): string {
    switch (estado.toLowerCase()) {
      case 'preparacion': return 'badge-secondary';
      case 'en_transito': return 'badge-info';
      case 'entregado': return 'badge-success';
      case 'retrasado': return 'badge-warning';
      case 'cancelado': return 'badge-danger';
      default: return 'badge-secondary';
    }
  }

  getTempStatus(temp?: number): { label: string; class: string } {
    if (temp === undefined || temp === null) return { label: 'N/A', class: 'telemetry-normal' };
    if (temp > 30 || temp < -5) return { label: `${temp}°C (Alerta)`, class: 'telemetry-danger' };
    return { label: `${temp}°C (Óptimo)`, class: 'telemetry-normal' };
  }

  getVibeStatus(vibe?: number): { label: string; class: string } {
    if (vibe === undefined || vibe === null) return { label: 'N/A', class: 'telemetry-normal' };
    if (vibe > 2.0) return { label: `${vibe}G (Impacto)`, class: 'telemetry-danger' };
    return { label: `${vibe}G (Estable)`, class: 'telemetry-normal' };
  }
}
