import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import {
  Plan,
  PlanCreate,
  PlanUpdate,
  PlanListResponse,
  Suscripcion,
  SuscripcionListResponse,
  SuscribirEmpresaRequest,
  CambiarPlanRequest,
  UpdateSuscripcionEstadoRequest
} from '../../models/subscription.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SubscriptionService {
  private http = inject(HttpClient);
  private planesUrl = `${environment.apiUrl}/planes`;
  private subsUrl = `${environment.apiUrl}/suscripciones`;

  planesSignal = signal<Plan[]>([]);
  suscripcionesSignal = signal<Suscripcion[]>([]);
  miSuscripcionSignal = signal<Suscripcion | null>(null);
  isLoadingSignal = signal<boolean>(false);

  // ==========================================
  // CU-036: PLANES DE SUSCRIPCIÓN
  // ==========================================
  getPlanes(soloActivos: boolean = false): Observable<PlanListResponse> {
    this.isLoadingSignal.set(true);
    let params = new HttpParams();
    if (soloActivos) {
      params = params.set('solo_activos', 'true');
    }
    return this.http.get<PlanListResponse>(this.planesUrl, { params }).pipe(
      tap((res) => {
        this.planesSignal.set(res.items);
        this.isLoadingSignal.set(false);
      })
    );
  }

  getPlanById(idplan: number): Observable<Plan> {
    return this.http.get<Plan>(`${this.planesUrl}/${idplan}`);
  }

  createPlan(data: PlanCreate): Observable<Plan> {
    return this.http.post<Plan>(this.planesUrl, data);
  }

  updatePlan(idplan: number, data: PlanUpdate): Observable<Plan> {
    return this.http.put<Plan>(`${this.planesUrl}/${idplan}`, data);
  }

  togglePlanEstado(idplan: number, activo: boolean): Observable<Plan> {
    return this.http.patch<Plan>(`${this.planesUrl}/${idplan}/estado`, { activo });
  }

  // ==========================================
  // CU-037: SUSCRIPCIONES
  // ==========================================
  getMiSuscripcion(): Observable<Suscripcion> {
    this.isLoadingSignal.set(true);
    return this.http.get<Suscripcion>(`${this.subsUrl}/actual`).pipe(
      tap((res) => {
        this.miSuscripcionSignal.set(res);
        this.isLoadingSignal.set(false);
      })
    );
  }

  getSuscripciones(params?: {
    idtenant?: number;
    estado?: string;
    idplan?: number;
    skip?: number;
    limit?: number;
  }): Observable<SuscripcionListResponse> {
    this.isLoadingSignal.set(true);
    let httpParams = new HttpParams();
    if (params?.idtenant) httpParams = httpParams.set('idtenant', params.idtenant.toString());
    if (params?.estado) httpParams = httpParams.set('estado', params.estado);
    if (params?.idplan) httpParams = httpParams.set('idplan', params.idplan.toString());
    if (params?.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());

    return this.http.get<SuscripcionListResponse>(this.subsUrl, { params: httpParams }).pipe(
      tap((res) => {
        this.suscripcionesSignal.set(res.items);
        this.isLoadingSignal.set(false);
      })
    );
  }

  suscribirEmpresa(data: SuscribirEmpresaRequest): Observable<Suscripcion> {
    return this.http.post<Suscripcion>(this.subsUrl, data);
  }

  cambiarPlan(idsuscripcion: number, data: CambiarPlanRequest): Observable<Suscripcion> {
    return this.http.put<Suscripcion>(`${this.subsUrl}/${idsuscripcion}/cambiar-plan`, data);
  }

  updateEstadoSuscripcion(idsuscripcion: number, data: UpdateSuscripcionEstadoRequest): Observable<Suscripcion> {
    return this.http.patch<Suscripcion>(`${this.subsUrl}/${idsuscripcion}/estado`, data);
  }
}

