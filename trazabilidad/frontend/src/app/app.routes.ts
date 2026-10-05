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
import { PurchaseManagementController } from './controllers/pages/purchase-management.controller';
import { ReceptionManagementController } from './controllers/pages/reception-management.controller';
import { QrManagementController } from './controllers/pages/qr-management.controller';
import { TransportManagementController } from './controllers/pages/transport-management.controller';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginController },
  { path: 'forgot-password', component: ForgotPasswordController },
  { path: 'reset-password', component: ResetPasswordController },
  { path: 'dashboard', component: DashboardController, canActivate: [authGuard] },
  { path: 'tenants', component: TenantManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa'])] },
  { path: 'users', component: UserManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa'])] },
  { path: 'roles', component: RoleManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa'])] },
  { path: 'bitacora', component: AuditNotificationController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'Auditor'])] },
  { path: 'categories', component: CategoryManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones'])] },
  { path: 'products', component: ProductManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones', 'GestorVentasPostventa'])] },
  { path: 'certifications', component: CertificationManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones'])] },
  { path: 'tenant-catalog', component: TenantCatalogManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones', 'GestorVentasPostventa'])] },
  { path: 'actors', component: ActorManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones'])] },
  { path: 'locations', component: LocationManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones'])] },
  { path: 'units', component: UnitManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones', 'GestorVentasPostventa', 'Auditor'])] },
  { path: 'purchases', component: PurchaseManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones', 'GestorVentasPostventa'])] },
  { path: 'receptions', component: ReceptionManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones'])] },
  { path: 'qr-codes', component: QrManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones', 'GestorVentasPostventa'])] },
  { path: 'shipments', component: TransportManagementController, canActivate: [authGuard, roleGuard(['SuperAdministrador', 'AdministradorEmpresa', 'GestorOperaciones', 'Auditor'])] },
  { path: '**', redirectTo: 'login' }
];
