import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { User, UserCreate, UserUpdate, UserListResponse } from '../../models/auth.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/users`;

  usersSignal = signal<User[]>([]);
  totalUsersSignal = signal<number>(0);
  isLoadingSignal = signal<boolean>(false);

  getUsers(search: string = '', tenantId?: number, skip: number = 0, limit: number = 50): Observable<UserListResponse> {
    this.isLoadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (search.trim()) {
      params = params.set('search', search.trim());
    }

    if (tenantId) {
      params = params.set('tenant_id', tenantId.toString());
    }

    return this.http.get<UserListResponse>(this.apiUrl, { params }).pipe(
      tap((response: UserListResponse) => {
        this.usersSignal.set(response.items);
        this.totalUsersSignal.set(response.total);
        this.isLoadingSignal.set(false);
      })
    );
  }

  getUserById(idusuario: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${idusuario}`);
  }

  createUser(data: UserCreate): Observable<User> {
    return this.http.post<User>(this.apiUrl, data);
  }

  updateUser(idusuario: number, data: UserUpdate): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${idusuario}`, data);
  }

  deleteUser(idusuario: number): Observable<User> {
    return this.http.delete<User>(`${this.apiUrl}/${idusuario}`);
  }
}
