import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

/**
 * COMPONENT-2 (tasarim_mimari.md): Yonetici Dashboard'u.
 * Faz 5'te iskelet (guard + oturum bilgisi); asil icerik (ihlal listesi,
 * istatistik grafigi, reddetme aksiyonu) Faz 6'da eklenecek.
 */
@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.scss',
})
export class AdminDashboard {
  protected readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  cikisYap(): void {
    this.authService.logout();
    this.router.navigate(['/giris']);
  }
}
