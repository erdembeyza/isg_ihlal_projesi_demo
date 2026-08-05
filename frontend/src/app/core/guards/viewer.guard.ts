import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const viewerGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isLoggedIn()) {
    return router.createUrlTree(['/']);
  }

  if (authService.isGoruntuleyici()) {
    return true;
  }

  if (authService.isYonetici()) {
    return router.createUrlTree(['/yonetici']);
  }

  return router.createUrlTree(['/formen']);
};
