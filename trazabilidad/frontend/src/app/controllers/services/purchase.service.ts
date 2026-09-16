import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { CompraItem, CompraListResponse, ActionPurchaseResponse } from '../../models/purchase.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PurchaseService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/purchases`;

  purchasesSignal = signal<CompraItem[]>([]);
  totalSignal = signal<number>(0);
  loadingSignal = signal<boolean>(false);

  getPurchases(estado: string = '', skip: number = 0, limit: number = 50): Observable<CompraListResponse> {
    this.loadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (estado) params = params.set('estado', estado);

    return this.http.get<CompraListResponse>(this.apiUrl, { params }).pipe(
      tap({
        next: (res) => {
          this.purchasesSignal.set(res.items);
          this.totalSignal.set(res.total);
          this.loadingSignal.set(false);
        },
        error: () => this.loadingSignal.set(false)
      })
    );
  }

  getPurchaseDetail(idcompra: number): Observable<CompraItem> {
    return this.http.get<CompraItem>(`${this.apiUrl}/${idcompra}`);
  }

  approvePurchase(idcompra: number): Observable<ActionPurchaseResponse> {
    return this.http.patch<ActionPurchaseResponse>(`${this.apiUrl}/${idcompra}/approve`, {});
  }

  rejectPurchase(idcompra: number, motivo: string): Observable<ActionPurchaseResponse> {
    return this.http.patch<ActionPurchaseResponse>(`${this.apiUrl}/${idcompra}/reject`, { motivo });
  }
}
