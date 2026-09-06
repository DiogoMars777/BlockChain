import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Tenant, TenantCreate, TenantUpdate, TenantListResponse } from '../../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class TenantService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api/v1/tenants';

  tenantsSignal = signal<Tenant[]>([]);
  totalTenantsSignal = signal<number>(0);
  isLoadingSignal = signal<boolean>(false);

  getTenants(search: string = '', skip: number = 0, limit: number = 50): Observable<TenantListResponse> {
    this.isLoadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (search.trim()) {
      params = params.set('search', search.trim());
    }

    return this.http.get<TenantListResponse>(this.apiUrl, { params }).pipe(
      tap((response: TenantListResponse) => {
        this.tenantsSignal.set(response.items);
        this.totalTenantsSignal.set(response.total);
        this.isLoadingSignal.set(false);
      })
    );
  }

  getTenantById(idtenant: number): Observable<Tenant> {
    return this.http.get<Tenant>(`${this.apiUrl}/${idtenant}`);
  }

  createTenant(data: TenantCreate): Observable<Tenant> {
    return this.http.post<Tenant>(this.apiUrl, data);
  }

  updateTenant(idtenant: number, data: TenantUpdate): Observable<Tenant> {
    return this.http.put<Tenant>(`${this.apiUrl}/${idtenant}`, data);
  }

  deleteTenant(idtenant: number): Observable<Tenant> {
    return this.http.delete<Tenant>(`${this.apiUrl}/${idtenant}`);
  }
}
