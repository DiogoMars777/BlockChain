import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Role, Permission, RolePermissionsResponse, UserRolesResponse } from '../../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class RoleService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api/v1';

  rolesSignal = signal<Role[]>([]);
  permissionsSignal = signal<Permission[]>([]);
  isLoadingSignal = signal<boolean>(false);

  getRoles(): Observable<Role[]> {
    this.isLoadingSignal.set(true);
    return this.http.get<Role[]>(`${this.apiUrl}/roles`).pipe(
      tap((roles) => {
        this.rolesSignal.set(roles);
        this.isLoadingSignal.set(false);
      })
    );
  }

  getPermissions(): Observable<Permission[]> {
    return this.http.get<Permission[]>(`${this.apiUrl}/permissions`).pipe(
      tap((perms) => {
        this.permissionsSignal.set(perms);
      })
    );
  }

  getRolePermissions(idrol: number): Observable<RolePermissionsResponse> {
    return this.http.get<RolePermissionsResponse>(`${this.apiUrl}/roles/${idrol}/permissions`);
  }

  getUserRoles(idusuario: number): Observable<UserRolesResponse> {
    return this.http.get<UserRolesResponse>(`${this.apiUrl}/users/${idusuario}/roles`);
  }

  assignUserRoles(idusuario: number, roleIds: number[]): Observable<UserRolesResponse> {
    return this.http.post<UserRolesResponse>(`${this.apiUrl}/users/${idusuario}/roles`, {
      role_ids: roleIds
    });
  }
}
