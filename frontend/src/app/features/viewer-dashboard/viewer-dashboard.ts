import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { interval } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { IhlalService } from '../../core/services/ihlal.service';
import {
  HaftalikRaporOzet,
  Ihlal,
  IhlalIstatistik,
  IslemLog,
  KaliteIstatistik,
  KameraDurum,
} from '../../core/models/ihlal.model';
import { IhlalListesiComponent } from '../../shared/components/ihlal-listesi/ihlal-listesi';
import { IstatistikGrafikComponent } from '../../shared/components/istatistik-grafik/istatistik-grafik';
import { IhlalDetayModalComponent } from '../../shared/components/ihlal-detay-modal/ihlal-detay-modal';
import { KameraDurumPaneliComponent } from '../../shared/components/kamera-durum-paneli/kamera-durum-paneli';
import { DenetimGunluguComponent } from '../../shared/components/denetim-gunlugu/denetim-gunlugu';
import { KaliteGrafikComponent } from '../../shared/components/kalite-grafik/kalite-grafik';
import { PanelShell } from '../../shared/layout/panel-shell/panel-shell';

const TUMU = 'TÜMÜ';
const CANLI_YENILEME_MS = 3000;

/** Salt-okunur üst yönetim / misafir paneli. */
@Component({
  selector: 'app-viewer-dashboard',
  standalone: true,
  imports: [
    IhlalListesiComponent,
    IstatistikGrafikComponent,
    IhlalDetayModalComponent,
    KameraDurumPaneliComponent,
    DenetimGunluguComponent,
    KaliteGrafikComponent,
    PanelShell,
  ],
  templateUrl: './viewer-dashboard.html',
  styleUrl: './viewer-dashboard.scss',
})
export class ViewerDashboard {
  protected readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly ihlalService = inject(IhlalService);

  protected readonly TUMU = TUMU;
  protected readonly ihlaller = signal<Ihlal[]>([]);
  protected readonly istatistikler = signal<IhlalIstatistik[]>([]);
  protected readonly kameralar = signal<KameraDurum[]>([]);
  protected readonly loglar = signal<IslemLog[]>([]);
  protected readonly kalite = signal<KaliteIstatistik | null>(null);
  protected readonly raporOzet = signal<HaftalikRaporOzet | null>(null);
  protected readonly yukleniyor = signal(true);
  protected readonly hataMesaji = signal<string | null>(null);
  protected readonly pdfIndiriliyor = signal(false);
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

  constructor() {
    this.verileriYukle(true);
    interval(CANLI_YENILEME_MS)
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.verileriYukle(false));
  }

  private verileriYukle(ilkYukleme = false): void {
    if (ilkYukleme) this.yukleniyor.set(true);
    this.ihlalService.listele().subscribe({
      next: (ihlaller) => {
        this.ihlaller.set(ihlaller);
        this.yukleniyor.set(false);
      },
      error: () => {
        if (ilkYukleme) {
          this.hataMesaji.set('Veriler yüklenemedi.');
          this.yukleniyor.set(false);
        }
      },
    });
    this.ihlalService.istatistik().subscribe({ next: (v) => this.istatistikler.set(v) });
    this.ihlalService.kameraDurumlari().subscribe({ next: (k) => this.kameralar.set(k) });
    this.ihlalService.islemLoglari(50).subscribe({ next: (l) => this.loglar.set(l) });
    this.ihlalService.kaliteIstatistik().subscribe({ next: (k) => this.kalite.set(k) });
    this.ihlalService.haftalikRaporOzet().subscribe({ next: (r) => this.raporOzet.set(r) });
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

  pdfIndir(): void {
    this.pdfIndiriliyor.set(true);
    this.ihlalService.haftalikRaporPdf().subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'haftalik-ihlal-raporu.pdf';
        a.click();
        URL.revokeObjectURL(url);
        this.pdfIndiriliyor.set(false);
      },
      error: () => {
        this.pdfIndiriliyor.set(false);
        this.hataMesaji.set('PDF indirilemedi.');
      },
    });
  }

  cikisYap(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
