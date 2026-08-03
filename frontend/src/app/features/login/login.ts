import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';

/**
 * COMPONENT-1 (tasarim_mimari.md): kullanici adi/sifre ile giris formu.
 * Basarili girişte rolune gore ilgili panele yonlendirir.
 */
@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  readonly gonderiliyor = signal(false);
  readonly hataMesaji = signal<string | null>(null);

  readonly form = this.fb.nonNullable.group({
    kullaniciAdi: ['', [Validators.required]],
    sifre: ['', [Validators.required]],
  });

  girisYap(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.gonderiliyor.set(true);
    this.hataMesaji.set(null);

    this.authService.login(this.form.getRawValue()).subscribe({
      next: (yanit) => {
        this.gonderiliyor.set(false);
        this.router.navigate([yanit.rol === 'ISG_YONETICI' ? '/yonetici' : '/formen']);
      },
      error: (hata: HttpErrorResponse) => {
        this.gonderiliyor.set(false);
        this.hataMesaji.set(
          hata.status === 401
            ? 'Kullanici adi veya sifre hatali.'
            : 'Giris yapilamadi, lutfen daha sonra tekrar deneyin.'
        );
      },
    });
  }
}
