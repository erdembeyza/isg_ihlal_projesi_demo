import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

/**
 * COMPONENT-3 (tasarim_mimari.md): Formen Dashboard'u.
 * Faz 5'te iskelet (guard + oturum bilgisi); asil icerik (kendi bolgesinin
 * blurlu ihlal listesi + trend ozeti) Faz 6'da eklenecek.
 */
@Component({
  selector: 'app-foreman-dashboard',
  standalone: true,
  templateUrl: './foreman-dashboard.html',
  styleUrl: './foreman-dashboard.scss',
})
export class ForemanDashboard {
  protected readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  cikisYap(): void {
    this.authService.logout();
    this.router.navigate(['/giris']);
  }
}
