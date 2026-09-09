import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { BitacoraItem, BitacoraListResponse, NotificacionItem, NotificacionListResponse } from '../../models/auth.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuditNotificationService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  bitacoraSignal = signal<BitacoraItem[]>([]);
  totalBitacoraSignal = signal<number>(0);
  notificationsSignal = signal<NotificacionItem[]>([]);
  unreadCountSignal = signal<number>(0);
  isLoadingSignal = signal<boolean>(false);

  getBitacora(accion: string = '', entidad: string = '', skip: number = 0, limit: number = 50): Observable<BitacoraListResponse> {
    this.isLoadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (accion.trim()) params = params.set('accion', accion.trim());
    if (entidad.trim()) params = params.set('entidad', entidad.trim());

    return this.http.get<BitacoraListResponse>(`${this.apiUrl}/bitacora`, { params }).pipe(
      tap((res) => {
        this.bitacoraSignal.set(res.items);
        this.totalBitacoraSignal.set(res.total);
        this.isLoadingSignal.set(false);
      })
    );
  }

  getNotifications(onlyUnread: boolean = false): Observable<NotificacionListResponse> {
    const params = new HttpParams().set('only_unread', onlyUnread.toString());
    return this.http.get<NotificacionListResponse>(`${this.apiUrl}/notifications`, { params }).pipe(
      tap((res) => {
        this.notificationsSignal.set(res.items);
        this.unreadCountSignal.set(res.unread_count);
      })
    );
  }

  markAsRead(idnotificacion: number): Observable<NotificacionItem> {
    return this.http.patch<NotificacionItem>(`${this.apiUrl}/notifications/${idnotificacion}/read`, {}).pipe(
      tap(() => {
        // Refresh notifications
        this.getNotifications().subscribe();
      })
    );
  }
}
