import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * MODUL-3 (tasarim_mimari.md): "HTTP Interceptor her isteğin Authorization
 * header'ına Bearer token ekler". /api/auth/login isteğine token eklenmez
 * (henuz token yok). 401 donen bir istek varsa (token gecersiz/suresi dolmus)
 * oturum temizlenip giris ekranina yonlendirilir.
 */
export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const token = authService.getToken();

  const istek = token && !req.url.includes('/auth/login')
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(istek).pipe(
    catchError((hata: HttpErrorResponse) => {
      const loginIstegi = req.url.includes('/auth/login');
      if (hata.status === 401 && !loginIstegi) {
        authService.logout();
        router.navigate(['/']);
      }
      return throwError(() => hata);
    })
  );
};
