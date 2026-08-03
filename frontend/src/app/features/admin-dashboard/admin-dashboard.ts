import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { BolgeService } from '../../core/services/bolge.service';
import { IhlalService } from '../../core/services/ihlal.service';
import { KullaniciService } from '../../core/services/kullanici.service';
import { Bolge } from '../../core/models/bolge.model';
import { Ihlal } from '../../core/models/ihlal.model';
import { Rol } from '../../core/models/auth.model';
import { IhlalListesiComponent } from '../../shared/components/ihlal-listesi/ihlal-listesi';
import { IstatistikGrafikComponent } from '../../shared/components/istatistik-grafik/istatistik-grafik';
import { IhlalDetayModalComponent } from '../../shared/components/ihlal-detay-modal/ihlal-detay-modal';

const TUMU = 'TÜMÜ';

/**
 * COMPONENT-2 (tasarim_mimari.md): Yonetici Dashboard'u.
 * Tum fabrika verisini (orijinal fotograflar) filtresiz ceker, bolge/tip
 * bazli filtreleme, istatistik grafigi, detay modali ve "Reddet" aksiyonunu
 * bir araya getirir. Ayrica MODUL-3 kapsaminda yeni formen/kullanici
 * tanimlama formunu barindirir (yalnizca ISG_YONETICI yetkili).
 */
@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [IhlalListesiComponent, IstatistikGrafikComponent, IhlalDetayModalComponent, ReactiveFormsModule],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.scss',
})
export class AdminDashboard {
  protected readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly ihlalService = inject(IhlalService);
  private readonly bolgeService = inject(BolgeService);
  private readonly kullaniciService = inject(KullaniciService);
  private readonly fb = inject(FormBuilder);

  protected readonly TUMU = TUMU;

  protected readonly ihlaller = signal<Ihlal[]>([]);
  protected readonly istatistikler = signal<import('../../core/models/ihlal.model').IhlalIstatistik[]>([]);
  protected readonly bolgeler = signal<Bolge[]>([]);
  protected readonly yukleniyor = signal(true);
  protected readonly hataMesaji = signal<string | null>(null);

  protected readonly secilenBolge = signal<string>(TUMU);
  protected readonly secilenTip = signal<string>(TUMU);
  protected readonly secilenIhlal = signal<Ihlal | null>(null);
  protected readonly reddetGonderiliyor = signal(false);

  protected readonly tipSecenekleri = computed(() => {
    const tipler = new Set(this.ihlaller().map((i) => i.ihlalTipiAdi));
    return [TUMU, ...tipler];
  });

  protected readonly filtreliIhlaller = computed(() => {
    const bolge = this.secilenBolge();
    const tip = this.secilenTip();
    return this.ihlaller().filter(
      (i) => (bolge === TUMU || i.bolgeAdi === bolge) && (tip === TUMU || i.ihlalTipiAdi === tip)
    );
  });

  protected readonly filtreliIstatistikler = computed(() => {
    const bolge = this.secilenBolge();
    return this.istatistikler().filter((i) => bolge === TUMU || i.bolgeAdi === bolge);
  });

  protected readonly kullaniciFormuAcik = signal(false);
  protected readonly kullaniciFormuGonderiliyor = signal(false);
  protected readonly kullaniciFormuMesaji = signal<{ tur: 'basari' | 'hata'; metin: string } | null>(null);

  protected readonly kullaniciForm = this.fb.nonNullable.group({
    kullaniciAdi: ['', [Validators.required, Validators.minLength(3)]],
    sifre: ['', [Validators.required, Validators.minLength(6)]],
    adSoyad: ['', [Validators.required]],
    rol: ['FORMEN' as Rol, [Validators.required]],
    bolgeId: [null as number | null],
  });

  constructor() {
    this.verileriYukle();
    this.bolgeService.listele().subscribe({ next: (bolgeler) => this.bolgeler.set(bolgeler) });
  }

  private verileriYukle(): void {
    this.yukleniyor.set(true);
    this.hataMesaji.set(null);

    this.ihlalService.listele().subscribe({
      next: (ihlaller) => {
        this.ihlaller.set(ihlaller);
        this.yukleniyor.set(false);
      },
      error: () => {
        this.hataMesaji.set('İhlal listesi yüklenemedi.');
        this.yukleniyor.set(false);
      },
    });

    this.ihlalService.istatistik().subscribe({ next: (veri) => this.istatistikler.set(veri) });
  }

  bolgeFiltresiDegisti(bolge: string): void {
    this.secilenBolge.set(bolge);
  }

  tipFiltresiDegisti(tip: string): void {
    this.secilenTip.set(tip);
  }

  grafiktenTipSecildi(tip: string): void {
    this.secilenTip.set(tip);
  }

  satirSecildi(ihlal: Ihlal): void {
    this.secilenIhlal.set(ihlal);
  }

  modaliKapat(): void {
    this.secilenIhlal.set(null);
  }

  ihlaliReddet(istek: { id: number; redNedeni: string | null }): void {
    this.reddetGonderiliyor.set(true);
    this.ihlalService.reddet(istek.id, { redNedeni: istek.redNedeni }).subscribe({
      next: () => {
        this.reddetGonderiliyor.set(false);
        this.secilenIhlal.set(null);
        this.verileriYukle();
      },
      error: () => {
        this.reddetGonderiliyor.set(false);
        this.hataMesaji.set('Reddetme işlemi başarısız oldu.');
      },
    });
  }

  kullaniciFormunuAcKapat(): void {
    this.kullaniciFormuAcik.set(!this.kullaniciFormuAcik());
    this.kullaniciFormuMesaji.set(null);
  }

  kullaniciOlustur(): void {
    if (this.kullaniciForm.invalid) {
      this.kullaniciForm.markAllAsTouched();
      return;
    }

    const deger = this.kullaniciForm.getRawValue();

    if (deger.rol === 'FORMEN' && !deger.bolgeId) {
      this.kullaniciFormuMesaji.set({ tur: 'hata', metin: 'Formen rolü için bölge seçimi zorunludur.' });
      return;
    }
    this.kullaniciFormuGonderiliyor.set(true);
    this.kullaniciFormuMesaji.set(null);

    this.kullaniciService
      .olustur({
        kullaniciAdi: deger.kullaniciAdi,
        sifre: deger.sifre,
        adSoyad: deger.adSoyad,
        rol: deger.rol,
        bolgeId: deger.rol === 'FORMEN' ? deger.bolgeId : null,
      })
      .subscribe({
        next: (yanit) => {
          this.kullaniciFormuGonderiliyor.set(false);
          this.kullaniciFormuMesaji.set({ tur: 'basari', metin: `"${yanit.kullaniciAdi}" kullanıcısı oluşturuldu.` });
          this.kullaniciForm.reset({ kullaniciAdi: '', sifre: '', adSoyad: '', rol: 'FORMEN', bolgeId: null });
        },
        error: (hata: HttpErrorResponse) => {
          this.kullaniciFormuGonderiliyor.set(false);
          this.kullaniciFormuMesaji.set({
            tur: 'hata',
            metin: hata.status === 409 ? 'Bu kullanıcı adı zaten kayıtlı.' : 'Kullanıcı oluşturulamadı.',
          });
        },
      });
  }

  cikisYap(): void {
    this.authService.logout();
    this.router.navigate(['/giris']);
  }
}
