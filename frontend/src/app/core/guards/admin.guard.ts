import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * COMPONENT-2 (tasarim_mimari.md): "AdminGuard ile yalnizca ISG_YONETICI
 * rolune erisim izni verir". Oturum yoksa login'e, oturum var ama rol
 * uygun degilse (ör. formen admin sayfasina gitmeye calisirsa) kendi
 * paneline geri yonlendirir.
 */
export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isLoggedIn()) {
    return router.createUrlTree(['/']);
  }

  if (authService.isYonetici()) {
    return true;
  }

  return router.createUrlTree(['/formen']);
};
