import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, effect, inject, input, output, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../../core/services/auth.service';
import { Profil, rolEtiketi } from '../../../core/models/auth.model';

@Component({
  selector: 'app-profil-paneli',
  standalone: true,
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './profil-paneli.html',
  styleUrl: './profil-paneli.scss',
})
export class ProfilPaneliComponent {
  private readonly authService = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  readonly acik = input(false);
  readonly cikis = output<void>();
  readonly kapandi = output<void>();

  protected readonly rolEtiketi = rolEtiketi;

  protected readonly profil = signal<Profil | null>(null);
  protected readonly yukleniyor = signal(false);
  protected readonly mesaj = signal<{ tur: 'basari' | 'hata'; metin: string } | null>(null);
  protected readonly kaydediliyor = signal(false);

  protected readonly profilForm = this.fb.nonNullable.group({
    adSoyad: ['', [Validators.required, Validators.maxLength(100)]],
  });

  protected readonly sifreForm = this.fb.nonNullable.group({
    mevcutSifre: ['', [Validators.required]],
    yeniSifre: ['', [Validators.required, Validators.minLength(6)]],
    yeniSifreTekrar: ['', [Validators.required]],
  });

  constructor() {
    effect(() => {
      if (this.acik()) {
        this.verileriYukle();
      } else {
        this.temizle();
      }
    });
  }

  arkaPlanaTiklandi(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.kapat();
    }
  }

  kapat(): void {
    this.kapandi.emit();
  }

  profilKaydet(): void {
    if (this.profilForm.invalid) {
      this.profilForm.markAllAsTouched();
      return;
    }
    this.kaydediliyor.set(true);
    this.mesaj.set(null);
    this.authService.profilGuncelle({ adSoyad: this.profilForm.controls.adSoyad.value }).subscribe({
      next: (profil) => {
        this.profil.set(profil);
        this.kaydediliyor.set(false);
        this.mesaj.set({ tur: 'basari', metin: 'Profil bilgileriniz güncellendi.' });
      },
      error: () => {
        this.kaydediliyor.set(false);
        this.mesaj.set({ tur: 'hata', metin: 'Profil güncellenemedi.' });
      },
    });
  }

  sifreDegistir(): void {
    if (this.sifreForm.invalid) {
      this.sifreForm.markAllAsTouched();
      return;
    }
    const deger = this.sifreForm.getRawValue();
    if (deger.yeniSifre !== deger.yeniSifreTekrar) {
      this.mesaj.set({ tur: 'hata', metin: 'Yeni parolalar eşleşmiyor.' });
      return;
    }
    this.kaydediliyor.set(true);
    this.mesaj.set(null);
    this.authService
      .sifreDegistir({ mevcutSifre: deger.mevcutSifre, yeniSifre: deger.yeniSifre })
      .subscribe({
        next: () => {
          this.kaydediliyor.set(false);
          this.sifreForm.reset();
          this.mesaj.set({ tur: 'basari', metin: 'Parolanız güncellendi.' });
        },
        error: (hata: HttpErrorResponse) => {
          this.kaydediliyor.set(false);
          this.mesaj.set({
            tur: 'hata',
            metin: hata.status === 400 ? 'Mevcut parola hatalı veya yeni parola geçersiz.' : 'Parola güncellenemedi.',
          });
        },
      });
  }

  cikisYap(): void {
    this.cikis.emit();
  }

  private verileriYukle(): void {
    this.yukleniyor.set(true);
    this.mesaj.set(null);
    this.authService.profilGetir().subscribe({
      next: (profil) => {
        this.profil.set(profil);
        this.profilForm.patchValue({ adSoyad: profil.adSoyad });
        this.yukleniyor.set(false);
      },
      error: () => {
        this.yukleniyor.set(false);
        this.mesaj.set({ tur: 'hata', metin: 'Profil bilgileri yüklenemedi.' });
      },
    });
  }

  private temizle(): void {
    this.mesaj.set(null);
    this.sifreForm.reset();
  }
}
