import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { RoleService } from '../services/role.service';
import { UserService } from '../services/user.service';
import { Role, Permission, User } from '../../models/auth.models';

@Component({
  selector: 'app-role-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: '../../views/pages/role-management.view.html',
  styleUrls: ['../../views/pages/role-management.view.css']
})
export class RoleManagementController implements OnInit {
  private roleService = inject(RoleService);
  private userService = inject(UserService);
  private router = inject(Router);

  roles = this.roleService.rolesSignal;
  permissions = this.roleService.permissionsSignal;
  users = this.userService.usersSignal;
  isLoading = this.roleService.isLoadingSignal;

  selectedUser = signal<User | null>(null);
  selectedRoleIds = signal<number[]>([]);
  selectedRoleForDetail = signal<Role | null>(null);
  rolePermissionsList = signal<Permission[]>([]);

  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.roleService.getRoles().subscribe();
    this.roleService.getPermissions().subscribe();
    this.userService.getUsers().subscribe();
  }

  onSelectUser(user: User): void {
    this.selectedUser.set(user);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    this.roleService.getUserRoles(user.idusuario).subscribe({
      next: (res) => {
        const ids = res.roles.map(r => r.idrol);
        this.selectedRoleIds.set(ids);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al obtener los roles del usuario.');
      }
    });
  }

  toggleRole(roleId: number): void {
    const current = [...this.selectedRoleIds()];
    const index = current.indexOf(roleId);
    if (index > -1) {
      current.splice(index, 1);
    } else {
      current.push(roleId);
    }
    this.selectedRoleIds.set(current);
  }

  isRoleSelected(roleId: number): boolean {
    return this.selectedRoleIds().includes(roleId);
  }

  onInspectRolePermissions(role: Role): void {
    this.selectedRoleForDetail.set(role);
    this.roleService.getRolePermissions(role.idrol).subscribe({
      next: (res) => {
        this.rolePermissionsList.set(res.permissions);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al consultar permisos.');
      }
    });
  }

  saveUserRoles(): void {
    if (!this.selectedUser()) {
      this.errorMessage.set('Seleccione un usuario primero.');
      return;
    }

    const userId = this.selectedUser()!.idusuario;
    const roleIds = this.selectedRoleIds();

    this.roleService.assignUserRoles(userId, roleIds).subscribe({
      next: () => {
        this.successMessage.set(`Roles actualizados correctamente para '${this.selectedUser()?.nombrecompleto}'.`);
        setTimeout(() => this.successMessage.set(null), 3000);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al guardar los roles.');
      }
    });
  }

  navigateToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }
}
