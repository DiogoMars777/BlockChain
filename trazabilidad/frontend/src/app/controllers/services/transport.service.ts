import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { EnvioItem, EnvioTimelineResponse, EventoTrazabilidadItem, CreateTransportEventPayload, EnvioDetalle, EnvioCreate, EnvioUpdate, EnvioUnidadesResponse, EnvioUnidadActionResponse } from '../../models/transport.model';
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

  getShipment(idenvio: number): Observable<EnvioDetalle> {
    return this.http.get<EnvioDetalle>(`${this.apiUrl}/${idenvio}`);
  }

  createShipment(data: EnvioCreate): Observable<EnvioDetalle> {
    this.loadingSignal.set(true);
    return this.http.post<EnvioDetalle>(this.apiUrl, data).pipe(
      tap({ error: () => this.loadingSignal.set(false) })
    );
  }

  updateShipment(idenvio: number, data: EnvioUpdate): Observable<EnvioDetalle> {
    this.loadingSignal.set(true);
    return this.http.put<EnvioDetalle>(`${this.apiUrl}/${idenvio}`, data).pipe(
      tap({ error: () => this.loadingSignal.set(false) })
    );
  }

  updateEstado(idenvio: number, estado: string): Observable<EnvioDetalle> {
    this.loadingSignal.set(true);
    return this.http.patch<EnvioDetalle>(`${this.apiUrl}/${idenvio}/estado`, { estado }).pipe(
      tap({ error: () => this.loadingSignal.set(false) })
    );
  }

  recordEvent(idenvio: number, payload: CreateTransportEventPayload): Observable<EventoTrazabilidadItem> {
    return this.http.post<EventoTrazabilidadItem>(`${this.apiUrl}/${idenvio}/events`, payload);
  }

  /** CU-020: unidades ya asignadas al envio y candidatas que se pueden asignar. */
  getShipmentUnits(idenvio: number): Observable<EnvioUnidadesResponse> {
    return this.http.get<EnvioUnidadesResponse>(`${this.apiUrl}/${idenvio}/units`);
  }

  assignUnit(idenvio: number, idunidad: number): Observable<EnvioUnidadActionResponse> {
    return this.http.post<EnvioUnidadActionResponse>(`${this.apiUrl}/${idenvio}/units`, { idunidad });
  }

  assignUnitsBulk(idenvio: number, unidades: number[]): Observable<EnvioUnidadActionResponse> {
    return this.http.post<EnvioUnidadActionResponse>(`${this.apiUrl}/${idenvio}/units/bulk`, { unidades });
  }

  unassignUnit(idenvio: number, idunidad: number): Observable<EnvioUnidadActionResponse> {
    return this.http.delete<EnvioUnidadActionResponse>(`${this.apiUrl}/${idenvio}/units/${idunidad}`);
  }
}
