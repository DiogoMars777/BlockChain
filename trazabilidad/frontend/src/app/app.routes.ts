import { Routes } from '@angular/router';
import { LoginController } from './controllers/auth/login.controller';
import { ForgotPasswordController } from './controllers/auth/forgot-password.controller';
import { ResetPasswordController } from './controllers/auth/reset-password.controller';
import { DashboardController } from './controllers/pages/dashboard.controller';
import { TenantManagementController } from './controllers/pages/tenant-management.controller';
import { UserManagementController } from './controllers/pages/user-management.controller';
import { RoleManagementController } from './controllers/pages/role-management.controller';
import { AuditNotificationController } from './controllers/pages/audit-notification.controller';
import { CategoryManagementController } from './controllers/pages/category-management.controller';
import { ProductManagementController } from './controllers/pages/product-management.controller';
import { CertificationManagementController } from './controllers/pages/certification-management.controller';
import { TenantCatalogManagementController } from './controllers/pages/tenant-catalog-management.controller';
import { ActorManagementController } from './controllers/pages/actor-management.controller';
import { LocationManagementController } from './controllers/pages/location-management.controller';
import { UnitManagementController } from './controllers/pages/unit-management.controller';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginController },
  { path: 'forgot-password', component: ForgotPasswordController },
  { path: 'reset-password', component: ResetPasswordController },
  { path: 'dashboard', component: DashboardController, canActivate: [authGuard] },
  { path: 'tenants', component: TenantManagementController, canActivate: [authGuard] },
  { path: 'users', component: UserManagementController, canActivate: [authGuard] },
  { path: 'roles', component: RoleManagementController, canActivate: [authGuard] },
  { path: 'bitacora', component: AuditNotificationController, canActivate: [authGuard] },
  { path: 'categories', component: CategoryManagementController, canActivate: [authGuard] },
  { path: 'products', component: ProductManagementController, canActivate: [authGuard] },
  { path: 'certifications', component: CertificationManagementController, canActivate: [authGuard] },
  { path: 'tenant-catalog', component: TenantCatalogManagementController, canActivate: [authGuard] },
  { path: 'actors', component: ActorManagementController, canActivate: [authGuard] },
  { path: 'locations', component: LocationManagementController, canActivate: [authGuard] },
  { path: 'units', component: UnitManagementController, canActivate: [authGuard] },
  { path: '**', redirectTo: 'login' }
];
