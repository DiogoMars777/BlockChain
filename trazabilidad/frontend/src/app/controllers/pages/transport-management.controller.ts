import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TransportService } from '../services/transport.service';
import { LocationService } from '../services/location.service';
import { EnvioItem, EnvioTimelineResponse, CreateTransportEventPayload } from '../../models/transport.model';
import { LocationItem } from '../../models/auth.models';

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

  shipments = this.transportService.shipmentsSignal;
  isLoading = this.transportService.loadingSignal;
  locations = this.locationService.locationsSignal;

  selectedEstado = signal<string>('');
  selectedShipment = signal<EnvioItem | null>(null);
  timelineData = signal<EnvioTimelineResponse | null>(null);

  isTimelineModalOpen = signal<boolean>(false);
  isRecordModalOpen = signal<boolean>(false);

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
