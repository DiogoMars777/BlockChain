import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { LocationItem, LocationCreate, LocationListResponse } from '../../models/auth.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LocationService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/locations`;

  locationsSignal = signal<LocationItem[]>([]);
  totalSignal = signal<number>(0);
  loadingSignal = signal<boolean>(false);

  getLocations(search: string = '', tipo: string = '', skip: number = 0, limit: number = 50): Observable<LocationListResponse> {
    this.loadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (search) params = params.set('search', search);
    if (tipo) params = params.set('tipo', tipo);

    return this.http.get<LocationListResponse>(this.apiUrl, { params }).pipe(
      tap({
        next: (res) => {
          this.locationsSignal.set(res.items);
          this.totalSignal.set(res.total);
          this.loadingSignal.set(false);
        },
        error: () => this.loadingSignal.set(false)
      })
    );
  }

  createLocation(data: LocationCreate): Observable<LocationItem> {
    return this.http.post<LocationItem>(this.apiUrl, data);
  }

  updateLocation(idubicacion: number, data: Partial<LocationCreate>): Observable<LocationItem> {
    return this.http.put<LocationItem>(`${this.apiUrl}/${idubicacion}`, data);
  }

  deleteLocation(idubicacion: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${idubicacion}`);
  }
}
