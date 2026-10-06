import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  PricingRecommendationRequest,
  PricingRecommendationsResponse
} from '../../models/recommendation.model';

@Injectable({
  providedIn: 'root'
})
export class RecommendationService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  recommendationsSignal = signal<PricingRecommendationsResponse | null>(null);
  isLoadingSignal = signal<boolean>(false);
  errorMessageSignal = signal<string | null>(null);

  generateRecommendations(top_n: number = 8, tenant_id?: number): Observable<PricingRecommendationsResponse> {
    this.isLoadingSignal.set(true);
    this.errorMessageSignal.set(null);

    const body: PricingRecommendationRequest = { top_n };
    if (tenant_id !== undefined && tenant_id !== null) {
      body.tenant_id = tenant_id;
    }
    return this.http
      .post<PricingRecommendationsResponse>(`${this.apiUrl}/tenant-catalog/recommendations`, body)
      .pipe(
        tap({
          next: (res) => {
            this.recommendationsSignal.set(res);
            this.isLoadingSignal.set(false);
          },
          error: (err) => {
            this.isLoadingSignal.set(false);
            this.errorMessageSignal.set(err.error?.detail || 'Error al generar recomendaciones con IA.');
          }
        })
      );
  }

  clear(): void {
    this.recommendationsSignal.set(null);
    this.errorMessageSignal.set(null);
    this.isLoadingSignal.set(false);
  }
}
