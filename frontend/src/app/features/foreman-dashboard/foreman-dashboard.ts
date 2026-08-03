import { Component, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { IhlalService } from '../../core/services/ihlal.service';
import { Ihlal, IhlalIstatistik } from '../../core/models/ihlal.model';
import { IhlalListesiComponent } from '../../shared/components/ihlal-listesi/ihlal-listesi';
import { IstatistikGrafikComponent } from '../../shared/components/istatistik-grafik/istatistik-grafik';
import { IhlalDetayModalComponent } from '../../shared/components/ihlal-detay-modal/ihlal-detay-modal';

const TUMU = 'TÜMÜ';

/**
 * COMPONENT-3 (tasarim_mimari.md): Formen Dashboard'u.
 * Backend (/api/ihlaller) JWT'deki bolgeId'ye gore zaten kapsami kendi
 * bolgesiyle ve fotograflari blurlu versiyonla sinirlar; bu bilesen ekstra
 * bir bolge filtresi uygulamaz, sadece ihlal tipine gore filtreler ve
 * "Reddet" aksiyonunu GOSTERMEZ (yalnizca ISG_YONETICI yetkilidir).
 */
@Component({
  selector: 'app-foreman-dashboard',
  standalone: true,
  imports: [IhlalListesiComponent, IstatistikGrafikComponent, IhlalDetayModalComponent],
  templateUrl: './foreman-dashboard.html',
  styleUrl: './foreman-dashboard.scss',
})
export class ForemanDashboard {
  protected readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly ihlalService = inject(IhlalService);

  protected readonly TUMU = TUMU;

  protected readonly ihlaller = signal<Ihlal[]>([]);
  protected readonly istatistikler = signal<IhlalIstatistik[]>([]);
  protected readonly yukleniyor = signal(true);
  protected readonly hataMesaji = signal<string | null>(null);

  protected readonly secilenTip = signal<string>(TUMU);
  protected readonly secilenIhlal = signal<Ihlal | null>(null);

  protected readonly tipSecenekleri = computed(() => {
    const tipler = new Set(this.ihlaller().map((i) => i.ihlalTipiAdi));
    return [TUMU, ...tipler];
  });

  protected readonly filtreliIhlaller = computed(() => {
    const tip = this.secilenTip();
    return this.ihlaller().filter((i) => tip === TUMU || i.ihlalTipiAdi === tip);
  });

  protected readonly enBelirginTrend = computed(() => {
    const veri = this.istatistikler();
    if (veri.length === 0) {
      return null;
    }
    return [...veri].sort((a, b) => Math.abs(b.yuzdeDegisim) - Math.abs(a.yuzdeDegisim))[0];
  });

  constructor() {
    this.verileriYukle();
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

  cikisYap(): void {
    this.authService.logout();
    this.router.navigate(['/giris']);
  }
}
