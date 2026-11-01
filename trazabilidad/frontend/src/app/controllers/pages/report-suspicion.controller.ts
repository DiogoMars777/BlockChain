import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { SuspicionService } from '../services/suspicion.service';
import { ReportarSospechaRequest, ReporteSospechaResponse } from '../../models/suspicion.model';

@Component({
  selector: 'app-report-suspicion',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/report-suspicion.view.html',
  styleUrls: ['../../views/pages/report-suspicion.view.css']
})
export class ReportSuspicionController implements OnInit {
  private suspicionService = inject(SuspicionService);
  private route = inject(ActivatedRoute);

  identificadorTipo = signal<'uuid' | 'serial'>('uuid');
  uuidpublico = signal('');
  numeroserie = signal('');
  motivo = signal('producto_falso');
  descripcion = signal('');
  evidencia = signal('');
  nombrereportante = signal('');
  contactoreportante = signal('');

  isSubmitting = signal(false);
  errorMessage = signal<string | null>(null);
  successResult = signal<ReporteSospechaResponse | null>(null);

  readonly motivos = [
    { value: 'producto_falso', label: 'Producto o dispositivo falsificado' },
    { value: 'empaque_alterado', label: 'Empaque o precinto de seguridad alterado / violado' },
    { value: 'serial_duplicado', label: 'Número de serie o IMEI duplicado en otro equipo' },
    { value: 'origen_dudoso', label: 'Procedencia o punto de venta no autorizado / dudoso' },
    { value: 'otro', label: 'Otro motivo (especificar en la descripción)' }
  ];

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      if (params['uuid']) {
        this.uuidpublico.set(params['uuid']);
        this.identificadorTipo.set('uuid');
      } else if (params['serial']) {
        this.numeroserie.set(params['serial']);
        this.identificadorTipo.set('serial');
      }
    });
  }

  setIdentificadorTipo(tipo: 'uuid' | 'serial'): void {
    this.identificadorTipo.set(tipo);
    this.errorMessage.set(null);
  }

  onSubmit(): void {
    this.errorMessage.set(null);

    const uuid = this.uuidpublico().trim();
    const serial = this.numeroserie().trim();

    if (this.identificadorTipo() === 'uuid' && !uuid) {
      this.errorMessage.set('Por favor, ingrese el código UUID público de la unidad o código QR.');
      return;
    }
    if (this.identificadorTipo() === 'serial' && !serial) {
      this.errorMessage.set('Por favor, ingrese el número de serie de la unidad.');
      return;
    }

    if (!this.descripcion().trim() && this.motivo() === 'otro') {
      this.errorMessage.set('Por favor, detalle la descripción cuando seleccione "Otro motivo".');
      return;
    }

    const payload: ReportarSospechaRequest = {
      uuidpublico: this.identificadorTipo() === 'uuid' ? uuid : undefined,
      numeroserie: this.identificadorTipo() === 'serial' ? serial : undefined,
      motivo: this.motivo(),
      descripcion: this.descripcion().trim() || undefined,
      evidencia: this.evidencia().trim() || undefined,
      nombrereportante: this.nombrereportante().trim() || undefined,
      contactoreportante: this.contactoreportante().trim() || undefined
    };

    this.isSubmitting.set(true);
    this.suspicionService.reportSuspicion(payload).subscribe({
      next: (res) => {
        this.isSubmitting.set(false);
        this.successResult.set(res);
      },
      error: (err) => {
        this.isSubmitting.set(false);
        const detail = err?.error?.detail || 'Ocurrió un error al registrar el reporte. Verifique los datos.';
        this.errorMessage.set(detail);
      }
    });
  }

  resetForm(): void {
    this.uuidpublico.set('');
    this.numeroserie.set('');
    this.motivo.set('producto_falso');
    this.descripcion.set('');
    this.evidencia.set('');
    this.nombrereportante.set('');
    this.contactoreportante.set('');
    this.errorMessage.set(null);
    this.successResult.set(null);
  }
}

