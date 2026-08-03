import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * COMPONENT-3 (tasarim_mimari.md): "ForemanGuard ile yalnizca FORMEN rolune
 * ... erisimi kisitlar". Bolge bazli kisit (token'daki bolgeId) backend
 * tarafinda IhlalService icinde zaten zorunlu kilinir; burada sadece rol
 * kontrolu yapilir.
 */
export const foremanGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isLoggedIn()) {
    return router.createUrlTree(['/giris']);
  }

  if (authService.isFormen()) {
    return true;
  }

  return router.createUrlTree(['/yonetici']);
};
