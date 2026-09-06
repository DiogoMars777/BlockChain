import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { UnitItem, UnitCreate, UnitListResponse } from '../../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class UnitService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api/v1/units';

  unitsSignal = signal<UnitItem[]>([]);
  totalSignal = signal<number>(0);
  loadingSignal = signal<boolean>(false);

  getUnits(search: string = '', estado: string = '', idvariante?: number, skip: number = 0, limit: number = 50): Observable<UnitListResponse> {
    this.loadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (search) params = params.set('search', search);
    if (estado) params = params.set('estado', estado);
    if (idvariante) params = params.set('idvariante', idvariante.toString());

    return this.http.get<UnitListResponse>(this.apiUrl, { params }).pipe(
      tap({
        next: (res) => {
          this.unitsSignal.set(res.items);
          this.totalSignal.set(res.total);
          this.loadingSignal.set(false);
        },
        error: () => this.loadingSignal.set(false)
      })
    );
  }

  createUnit(data: UnitCreate): Observable<UnitItem> {
    return this.http.post<UnitItem>(this.apiUrl, data);
  }

  updateUnit(idunidad: number, data: Partial<UnitCreate>): Observable<UnitItem> {
    return this.http.put<UnitItem>(`${this.apiUrl}/${idunidad}`, data);
  }

  deleteUnit(idunidad: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${idunidad}`);
  }
}
