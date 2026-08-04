import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * Genel oturum guard'i: gecerli bir oturum (JWT) yoksa giris ekranina yonlendirir.
 * Rol bazli kisitlar icin bkz. adminGuard / foremanGuard.
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  }

  return router.createUrlTree(['/']);
};
