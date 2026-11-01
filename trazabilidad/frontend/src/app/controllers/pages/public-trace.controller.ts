import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TraceService } from '../services/trace.service';
import { CertificateService } from '../services/certificate.service';
import { PublicTraceResponse } from '../../models/trace.model';
import { UnitCertificateResponse } from '../../models/certificate.model';

@Component({
  selector: 'app-public-trace',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: '../../views/pages/public-trace.view.html',
  styleUrls: ['../../views/pages/public-trace.view.css']
})
export class PublicTraceController implements OnInit {
  private traceService = inject(TraceService);
  private certificateService = inject(CertificateService);
  private route = inject(ActivatedRoute);

  trace = signal<PublicTraceResponse | null>(null);
  certificate = signal<UnitCertificateResponse | null>(null);
  isLoading = signal<boolean>(true);
  isLoadingCert = signal<boolean>(false);
  notFound = signal<boolean>(false);

  ngOnInit(): void {
    const uuid = this.route.snapshot.paramMap.get('uuid') || '';
    if (!uuid) {
      this.isLoading.set(false);
      this.notFound.set(true);
      return;
    }
    this.traceService.getTrace(uuid).subscribe({
      next: (res) => {
        this.trace.set(res);
        this.isLoading.set(false);
        this.loadCertificate(uuid);
      },
      error: () => {
        this.isLoading.set(false);
        this.notFound.set(true);
      }
    });
  }

  loadCertificate(uuid: string): void {
    this.isLoadingCert.set(true);
    this.certificateService.getPublicCertificate(uuid).subscribe({
      next: (res) => {
        this.certificate.set(res);
        this.isLoadingCert.set(false);
      },
      error: () => this.isLoadingCert.set(false)
    });
  }

  autenticidad(): 'verificado' | 'registrado' | 'sin_datos' {
    const t = this.trace();
    if (!t || t.eventos.length === 0) return 'sin_datos';
    const verificado = t.eventos.some(
      (e) => (e.estadoverificacion || '').toLowerCase().includes('verific')
    );
    return verificado ? 'verificado' : 'registrado';
  }
}
