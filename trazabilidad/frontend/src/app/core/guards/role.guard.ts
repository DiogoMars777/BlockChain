import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '../../controllers/services/auth.service';

export const roleGuard = (allowedRoles: string[]): CanActivateFn => {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);

    const user = authService.currentUser();
    const roles = user?.roles || [];

    if (roles.includes('SuperAdministrador')) {
      return true;
    }

    const hasAccess = allowedRoles.some(r => roles.includes(r));
    if (hasAccess) {
      return true;
    }

    return router.createUrlTree(['/dashboard']);
  };
};
