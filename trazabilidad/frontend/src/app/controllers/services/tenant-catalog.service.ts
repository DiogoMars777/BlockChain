import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import {
  TenantCatalogItem,
  TenantCatalogCreate,
  TenantCatalogUpdate,
  TenantCatalogListResponse
} from '../../models/auth.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TenantCatalogService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/tenant-catalog`;

  catalogSignal = signal<TenantCatalogItem[]>([]);
  totalCatalogSignal = signal<number>(0);
  isLoadingSignal = signal<boolean>(false);

  getCatalog(search: string = '', tenantId?: number, skip: number = 0, limit: number = 50): Observable<TenantCatalogListResponse> {
    this.isLoadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (search.trim()) params = params.set('search', search.trim());
    if (tenantId) params = params.set('tenant_id', tenantId.toString());

    return this.http.get<TenantCatalogListResponse>(this.apiUrl, { params }).pipe(
      tap((res) => {
        this.catalogSignal.set(res.items);
        this.totalCatalogSignal.set(res.total);
        this.isLoadingSignal.set(false);
      })
    );
  }

  addToCatalog(data: TenantCatalogCreate): Observable<TenantCatalogItem> {
    return this.http.post<TenantCatalogItem>(this.apiUrl, data);
  }

  updateCatalogItem(idcatalogotenant: number, data: TenantCatalogUpdate): Observable<TenantCatalogItem> {
    return this.http.put<TenantCatalogItem>(`${this.apiUrl}/${idcatalogotenant}`, data);
  }

  deleteCatalogItem(idcatalogotenant: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.apiUrl}/${idcatalogotenant}`);
  }
}
