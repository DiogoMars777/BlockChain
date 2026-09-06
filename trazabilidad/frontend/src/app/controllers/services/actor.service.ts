import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Actor, ActorCreate, ActorListResponse } from '../../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class ActorService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api/v1/actors';

  actorsSignal = signal<Actor[]>([]);
  totalSignal = signal<number>(0);
  loadingSignal = signal<boolean>(false);

  getActors(search: string = '', tipoactor: string = '', skip: number = 0, limit: number = 50): Observable<ActorListResponse> {
    this.loadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (search) params = params.set('search', search);
    if (tipoactor) params = params.set('tipoactor', tipoactor);

    return this.http.get<ActorListResponse>(this.apiUrl, { params }).pipe(
      tap({
        next: (res) => {
          this.actorsSignal.set(res.items);
          this.totalSignal.set(res.total);
          this.loadingSignal.set(false);
        },
        error: () => this.loadingSignal.set(false)
      })
    );
  }

  createActor(data: ActorCreate): Observable<Actor> {
    return this.http.post<Actor>(this.apiUrl, data);
  }

  updateActor(idactor: number, data: Partial<ActorCreate>): Observable<Actor> {
    return this.http.put<Actor>(`${this.apiUrl}/${idactor}`, data);
  }

  deleteActor(idactor: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${idactor}`);
  }
}
