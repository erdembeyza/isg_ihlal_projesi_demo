import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';
import { ExtranetShell } from '../../shared/layout/extranet-shell/extranet-shell';

/**
 * COMPONENT-1 (tasarim_mimari.md): Erdemir Online görünümünde giriş formu.
 * Ana sayfa ile aynı ekranı sunar; başarılı girişte rolüne göre panele yönlendirir.
 */
@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, ExtranetShell],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  readonly gonderiliyor = signal(false);
  readonly hataMesaji = signal<string | null>(null);
  readonly sifreGorunur = signal(false);
  readonly popItAcik = signal(false);
  readonly popItMesaji = signal('Yöneticiniz ile iletişime geçiniz.');

  readonly form = this.fb.nonNullable.group({
    kullaniciAdi: ['', [Validators.required]],
    sifre: ['', [Validators.required]],
  });

  sifreGorunurunuDegistir(): void {
    this.sifreGorunur.update((v) => !v);
  }

  popItGoster(mesaj = 'Yöneticiniz ile iletişime geçiniz.'): void {
    this.popItMesaji.set(mesaj);
    this.popItAcik.set(true);
  }

  popItKapat(): void {
    this.popItAcik.set(false);
  }

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
        if (yanit.rol === 'ISG_YONETICI') {
          this.router.navigate(['/yonetici']);
        } else if (yanit.rol === 'FORMEN') {
          this.router.navigate(['/formen']);
        } else {
          this.authService.logout();
          this.hataMesaji.set('Bu hesap panel girişi için kullanılamaz.');
        }
      },
      error: (hata: HttpErrorResponse) => {
        this.gonderiliyor.set(false);
        this.hataMesaji.set(
          hata.status === 401
            ? 'Kullanıcı adı veya parola hatalı.'
            : 'Giriş yapılamadı, lütfen daha sonra tekrar deneyin.'
        );
      },
    });
  }
}
