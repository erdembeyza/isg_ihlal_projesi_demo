import { Component, computed, inject, signal, viewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { interval } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { BolgeService } from '../../core/services/bolge.service';
import { IhlalService } from '../../core/services/ihlal.service';
import { Bolge } from '../../core/models/bolge.model';
import {
  HaftalikRaporOzet,
  Ihlal,
  IslemLog,
  KaliteIstatistik,
  KameraDurum,
  PersonelIstatistik,
} from '../../core/models/ihlal.model';
import { IhlalListesiComponent } from '../../shared/components/ihlal-listesi/ihlal-listesi';
import { IstatistikGrafikComponent } from '../../shared/components/istatistik-grafik/istatistik-grafik';
import { IhlalDetayModalComponent } from '../../shared/components/ihlal-detay-modal/ihlal-detay-modal';
import { KameraDurumPaneliComponent } from '../../shared/components/kamera-durum-paneli/kamera-durum-paneli';
import { DenetimGunluguComponent } from '../../shared/components/denetim-gunlugu/denetim-gunlugu';
import { KaliteGrafikComponent } from '../../shared/components/kalite-grafik/kalite-grafik';
import { PersonelIstatistikPaneliComponent } from '../../shared/components/personel-istatistik-paneli/personel-istatistik-paneli';
import { BolgeSaatOzetPaneliComponent } from '../../shared/components/bolge-saat-ozet-paneli/bolge-saat-ozet-paneli';
import { PanelShell } from '../../shared/layout/panel-shell/panel-shell';

const TUMU = 'TÜMÜ';
const CANLI_YENILEME_MS = 3000;

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    IhlalListesiComponent,
    IstatistikGrafikComponent,
    IhlalDetayModalComponent,
    KameraDurumPaneliComponent,
    DenetimGunluguComponent,
    KaliteGrafikComponent,
    PersonelIstatistikPaneliComponent,
    BolgeSaatOzetPaneliComponent,
    PanelShell,
  ],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.scss',
})
export class AdminDashboard {
  protected readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly ihlalService = inject(IhlalService);
  private readonly bolgeService = inject(BolgeService);
  private readonly panelShell = viewChild(PanelShell);

  protected readonly TUMU = TUMU;

  protected readonly ihlaller = signal<Ihlal[]>([]);
  protected readonly istatistikler = signal<import('../../core/models/ihlal.model').IhlalIstatistik[]>([]);
  protected readonly personelIstatistikleri = signal<PersonelIstatistik[]>([]);
  protected readonly bolgeler = signal<Bolge[]>([]);
  protected readonly kameralar = signal<KameraDurum[]>([]);
  protected readonly loglar = signal<IslemLog[]>([]);
  protected readonly kalite = signal<KaliteIstatistik | null>(null);
  protected readonly raporOzet = signal<HaftalikRaporOzet | null>(null);
  protected readonly yukleniyor = signal(true);
  protected readonly hataMesaji = signal<string | null>(null);
  protected readonly pdfIndiriliyor = signal(false);
  protected readonly senkronMesaji = signal<string | null>(null);
  /** Denetim günlüğü varsayılan kapalı; toggle ile açılır. */
  protected readonly denetimGunluguAcik = signal(false);

  protected readonly secilenBolge = signal<string>(TUMU);
  protected readonly secilenTip = signal<string>(TUMU);
  protected readonly baslangicTarihi = signal<string>('');
  protected readonly bitisTarihi = signal<string>('');
  protected readonly secilenIhlal = signal<Ihlal | null>(null);
  protected readonly reddetGonderiliyor = signal(false);

  protected readonly tipSecenekleri = computed(() => {
    const tipler = new Set(this.ihlaller().map((i) => i.ihlalTipiAdi));
    return [TUMU, ...tipler];
  });

  protected readonly filtreliIhlaller = computed(() => {
    const bolge = this.secilenBolge();
    const tip = this.secilenTip();
    const bas = this.baslangicTarihi();
    const bit = this.bitisTarihi();
    return this.ihlaller().filter((i) => {
      if (bolge !== TUMU && i.bolgeAdi !== bolge) return false;
      if (tip !== TUMU && i.ihlalTipiAdi !== tip) return false;
      if (bas && i.tespitZamani < `${bas}T00:00:00`) return false;
      if (bit && i.tespitZamani > `${bit}T23:59:59`) return false;
      return true;
    });
  });

  protected readonly filtreliIstatistikler = computed(() => {
    const bolge = this.secilenBolge();
    return this.istatistikler().filter((i) => bolge === TUMU || i.bolgeAdi === bolge);
  });

  constructor() {
    this.verileriYukle(true);
    this.bolgeService.listele().subscribe({ next: (bolgeler) => this.bolgeler.set(bolgeler) });
    interval(CANLI_YENILEME_MS)
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.verileriYukle(false));
  }

  private verileriYukle(ilkYukleme = false): void {
    if (ilkYukleme) {
      this.yukleniyor.set(true);
    }
    this.hataMesaji.set(null);

    this.ihlalService.listele().subscribe({
      next: (ihlaller) => {
        this.ihlaller.set(ihlaller);
        this.yukleniyor.set(false);
      },
      error: () => {
        if (ilkYukleme) {
          this.hataMesaji.set('İhlal listesi yüklenemedi.');
          this.yukleniyor.set(false);
        }
      },
    });

    this.ihlalService.istatistik().subscribe({ next: (veri) => this.istatistikler.set(veri) });
    this.ihlalService.personelIstatistik().subscribe({ next: (v) => this.personelIstatistikleri.set(v) });
    this.ihlalService.kameraDurumlari().subscribe({ next: (k) => this.kameralar.set(k) });
    this.ihlalService.islemLoglari(80).subscribe({ next: (l) => this.loglar.set(l) });
    this.ihlalService.kaliteIstatistik().subscribe({ next: (k) => this.kalite.set(k) });
    this.ihlalService.haftalikRaporOzet().subscribe({ next: (r) => this.raporOzet.set(r) });
  }

  bolgeFiltresiDegisti(bolge: string): void {
    this.secilenBolge.set(bolge);
  }

  tipFiltresiDegisti(tip: string): void {
    this.secilenTip.set(tip);
  }

  baslangicTarihiDegisti(tarih: string): void {
    this.baslangicTarihi.set(tarih);
  }

  bitisTarihiDegisti(tarih: string): void {
    this.bitisTarihi.set(tarih);
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

  finetuneSenkron(): void {
    this.senkronMesaji.set(null);
    this.ihlalService.finetuneSenkronize().subscribe({
      next: (r) => {
        this.senkronMesaji.set(
          `Fine-tune senkron: toplam ${r.toplam}, kopyalanan ${r.kopyalanan}, atlanan ${r.atlanan}`
        );
        this.ihlalService.kaliteIstatistik().subscribe({ next: (k) => this.kalite.set(k) });
      },
      error: () => this.senkronMesaji.set('Fine-tune senkron başarısız.'),
    });
  }

  denetimGunlugunuAcKapat(): void {
    this.denetimGunluguAcik.update((v) => !v);
  }

  kullaniciYonetiminiAc(): void {
    this.panelShell()?.kullaniciYonetiminiAc();
  }

  cikisYap(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
