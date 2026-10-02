import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import {
  RecepcionItem,
  RecepcionDetalle,
  RecepcionCreate,
  RecepcionActionResponse
} from '../../models/reception.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ReceptionService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/receptions`;

  recepcionesSignal = signal<RecepcionItem[]>([]);
  loadingSignal = signal<boolean>(false);

  getRecepciones(estado: string = '', idcompra?: number, skip: number = 0, limit: number = 50): Observable<RecepcionItem[]> {
    this.loadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (estado) params = params.set('estado', estado);
    if (idcompra) params = params.set('idcompra', idcompra.toString());

    return this.http.get<RecepcionItem[]>(this.apiUrl, { params }).pipe(
      tap({
        next: (res) => {
          this.recepcionesSignal.set(res);
          this.loadingSignal.set(false);
        },
        error: () => this.loadingSignal.set(false)
      })
    );
  }

  getRecepcion(idrecepcion: number): Observable<RecepcionDetalle> {
    return this.http.get<RecepcionDetalle>(`${this.apiUrl}/${idrecepcion}`);
  }

  createRecepcion(data: RecepcionCreate): Observable<RecepcionActionResponse> {
    return this.http.post<RecepcionActionResponse>(this.apiUrl, data);
  }

  updateEstado(idrecepcion: number, estado: string): Observable<RecepcionActionResponse> {
    return this.http.patch<RecepcionActionResponse>(`${this.apiUrl}/${idrecepcion}/estado`, { estado });
  }
}
