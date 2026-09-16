import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { EnvioItem, EnvioTimelineResponse, EventoTrazabilidadItem, CreateTransportEventPayload } from '../../models/transport.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TransportService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/shipments`;

  shipmentsSignal = signal<EnvioItem[]>([]);
  loadingSignal = signal<boolean>(false);

  getShipments(estado: string = '', skip: number = 0, limit: number = 50): Observable<EnvioItem[]> {
    this.loadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (estado) params = params.set('estado', estado);

    return this.http.get<EnvioItem[]>(this.apiUrl, { params }).pipe(
      tap({
        next: (res) => {
          this.shipmentsSignal.set(res);
          this.loadingSignal.set(false);
        },
        error: () => this.loadingSignal.set(false)
      })
    );
  }

  getTimeline(idenvio: number): Observable<EnvioTimelineResponse> {
    return this.http.get<EnvioTimelineResponse>(`${this.apiUrl}/${idenvio}/timeline`);
  }

  recordEvent(idenvio: number, payload: CreateTransportEventPayload): Observable<EventoTrazabilidadItem> {
    return this.http.post<EventoTrazabilidadItem>(`${this.apiUrl}/${idenvio}/events`, payload);
  }
}
