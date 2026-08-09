import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { interval } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { IhlalService } from '../../core/services/ihlal.service';
import {
  Ihlal,
  IhlalIstatistik,
  durumEtiketi,
} from '../../core/models/ihlal.model';
import { IhlalListesiComponent } from '../../shared/components/ihlal-listesi/ihlal-listesi';
import { IstatistikGrafikComponent } from '../../shared/components/istatistik-grafik/istatistik-grafik';
import { IhlalDetayModalComponent } from '../../shared/components/ihlal-detay-modal/ihlal-detay-modal';
import { PanelShell } from '../../shared/layout/panel-shell/panel-shell';

const TUMU = 'TÜMÜ';
const CANLI_YENILEME_MS = 3000;

type RiskDurumu = {
  etiket: string;
  seviye: 'stabil' | 'kritik';
};

type BolgeIhlalOzeti = {
  bolgeAdi: string;
  kisaAd: string;
  toplam: number;
  aktif: number;
  yuzde: number;
};

type YuksekFirinBolgeAnalizi = {
  bolgeler: BolgeIhlalOzeti[];
  enCok: BolgeIhlalOzeti;
  esitMi: boolean;
  toplam: number;
};

function yuksekFirinKisaAd(bolgeAdi: string): string | null {
  const ad = bolgeAdi.trim().toLocaleLowerCase('tr-TR');
  if (!ad.includes('fırın') && !ad.includes('firin')) {
    return null;
  }
  if (ad.includes('a bölgesi') || ad.includes('a bolgesi')) {
    return 'A Bölgesi';
  }
  if (ad.includes('b bölgesi') || ad.includes('b bolgesi')) {
    return 'B Bölgesi';
  }
  return null;
}

/**
 * COMPONENT-3 (tasarim_mimari.md): Formen Dashboard'u.
 * Backend (/api/ihlaller) JWT'deki bolgeId'ye gore zaten kapsami kendi
 * bolgesiyle sinirlar; bu bilesen ekstra
 * bir bolge filtresi uygulamaz, sadece ihlal tipine gore filtreler ve
 * "Reddet" aksiyonunu GOSTERMEZ (yalnizca ISG_YONETICI yetkilidir).
 */
@Component({
  selector: 'app-foreman-dashboard',
  standalone: true,
  imports: [IhlalListesiComponent, IstatistikGrafikComponent, IhlalDetayModalComponent, PanelShell],
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
  protected readonly cozuluyorId = signal<number | null>(null);
  protected readonly aksiyonHatasi = signal<string | null>(null);

  protected readonly secilenTip = signal<string>(TUMU);
  protected readonly baslangicTarihi = signal<string>('');
  protected readonly bitisTarihi = signal<string>('');
  protected readonly secilenIhlal = signal<Ihlal | null>(null);

  protected readonly tipSecenekleri = computed(() => {
    const tipler = new Set(this.ihlaller().map((i) => i.ihlalTipiAdi));
    return [TUMU, ...tipler];
  });

  protected readonly filtreliIhlaller = computed(() => {
    const tip = this.secilenTip();
    const bas = this.baslangicTarihi();
    const bit = this.bitisTarihi();
    return this.ihlaller().filter((i) => {
      if (tip !== TUMU && i.ihlalTipiAdi !== tip) return false;
      if (bas && i.tespitZamani < `${bas}T00:00:00`) return false;
      if (bit && i.tespitZamani > `${bit}T23:59:59`) return false;
      return true;
    });
  });

  protected readonly aktifIhlalSayisi = computed(
    () => this.ihlaller().filter((i) => i.durum === 'AKTIF').length
  );

  protected readonly bugunkuIhlalSayisi = computed(() => {
    const bugun = new Date();
    const yyyy = bugun.getFullYear();
    const mm = String(bugun.getMonth() + 1).padStart(2, '0');
    const dd = String(bugun.getDate()).padStart(2, '0');
    const gunPrefix = `${yyyy}-${mm}-${dd}`;
    return this.ihlaller().filter((i) => i.tespitZamani.startsWith(gunPrefix)).length;
  });

  protected readonly bolgeRisk = computed<RiskDurumu>(() => {
    const aktif = this.aktifIhlalSayisi();
    if (aktif >= 3) {
      return { etiket: 'Kritik', seviye: 'kritik' };
    }
    return { etiket: 'Stabil', seviye: 'stabil' };
  });

  protected readonly enBelirginTrend = computed(() => {
    const veri = this.istatistikler();
    if (veri.length === 0) {
      return null;
    }
    return [...veri].sort((a, b) => Math.abs(b.yuzdeDegisim) - Math.abs(a.yuzdeDegisim))[0];
  });

  /** Yüksek Fırın A/B formenleri için bölge bazlı ihlal analizi. */
  protected readonly yuksekFirinBolgeAnalizi = computed<YuksekFirinBolgeAnalizi | null>(() => {
    const harita = new Map<string, { bolgeAdi: string; kisaAd: string; toplam: number; aktif: number }>();

    const bolgeyiKaydet = (bolgeAdi: string) => {
      const kisaAd = yuksekFirinKisaAd(bolgeAdi);
      if (!kisaAd) {
        return null;
      }
      if (!harita.has(kisaAd)) {
        harita.set(kisaAd, { bolgeAdi, kisaAd, toplam: 0, aktif: 0 });
      }
      return kisaAd;
    };

    for (const istatistik of this.istatistikler()) {
      bolgeyiKaydet(istatistik.bolgeAdi);
    }

    for (const ihlal of this.ihlaller()) {
      const kisaAd = bolgeyiKaydet(ihlal.bolgeAdi);
      if (!kisaAd) {
        continue;
      }
      const mevcut = harita.get(kisaAd)!;
      mevcut.bolgeAdi = ihlal.bolgeAdi;
      mevcut.toplam += 1;
      if (ihlal.durum === 'AKTIF') {
        mevcut.aktif += 1;
      }
    }

    const aVar = harita.has('A Bölgesi');
    const bVar = harita.has('B Bölgesi');
    // Yüksek Fırın formenleri JWT'de A+B (2+ bolgeIds) taşır; demo'da çoklu bölge = YF.
    const cokluBolgeFormen = (this.authService.currentUser()?.bolgeIds?.length ?? 0) >= 2;
    if (!cokluBolgeFormen && !(aVar && bVar)) {
      return null;
    }

    const sablon: Array<{ kisaAd: string; varsayilanAd: string }> = [
      { kisaAd: 'A Bölgesi', varsayilanAd: 'Yüksek Fırın A Bolgesi' },
      { kisaAd: 'B Bölgesi', varsayilanAd: 'Yüksek Fırın B Bolgesi' },
    ];

    const toplam = [...harita.values()].reduce((s, b) => s + b.toplam, 0);
    const bolgeler: BolgeIhlalOzeti[] = sablon.map(({ kisaAd, varsayilanAd }) => {
      const kayit = harita.get(kisaAd);
      const adet = kayit?.toplam ?? 0;
      return {
        bolgeAdi: kayit?.bolgeAdi ?? varsayilanAd,
        kisaAd,
        toplam: adet,
        aktif: kayit?.aktif ?? 0,
        yuzde: toplam > 0 ? Math.round((adet / toplam) * 100) : 0,
      };
    });

    const sirali = [...bolgeler].sort((a, b) => b.toplam - a.toplam);
    const enCok = sirali[0];
    const esitMi = sirali[0].toplam === sirali[1].toplam;

    return { bolgeler, enCok, esitMi, toplam };
  });

  constructor() {
    this.verileriYukle(true);
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
        const secili = this.secilenIhlal();
        if (secili) {
          const guncel = ihlaller.find((i) => i.id === secili.id) ?? null;
          this.secilenIhlal.set(guncel);
        }
      },
      error: () => {
        if (ilkYukleme) {
          this.hataMesaji.set('İhlal listesi yüklenemedi.');
          this.yukleniyor.set(false);
        }
      },
    });

    this.ihlalService.istatistik().subscribe({ next: (veri) => this.istatistikler.set(veri) });
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

  ihlaliCoz(ihlal: Ihlal): void {
    const notHam = window.prompt(
      'Çözüm notu (opsiyonel — Enter ile boş bırakabilirsiniz):',
      ''
    );
    if (notHam === null) {
      return; // Vazgeçildi
    }
    const not = notHam.trim().slice(0, 500);

    this.aksiyonHatasi.set(null);
    this.cozuluyorId.set(ihlal.id);
    this.ihlalService.coz(ihlal.id, { not: not || null }).subscribe({
      next: (guncel) => {
        this.ihlaller.update((liste) => liste.map((i) => (i.id === guncel.id ? guncel : i)));
        if (this.secilenIhlal()?.id === guncel.id) {
          this.secilenIhlal.set(guncel);
        }
        this.cozuluyorId.set(null);
        this.ihlalService.istatistik().subscribe({ next: (veri) => this.istatistikler.set(veri) });
      },
      error: () => {
        this.cozuluyorId.set(null);
        this.aksiyonHatasi.set('İhlal çözüldü olarak işaretlenemedi.');
      },
    });
  }

  csvIndir(): void {
    const satirlar = this.filtreliIhlaller();
    const basliklar = [
      'ID',
      'Bölge',
      'Personel',
      'Sicil No',
      'İhlal Tipi',
      'Tespit Zamanı',
      'Durum',
    ];
    const csvSatirlari = [
      basliklar.join(';'),
      ...satirlar.map((i) =>
        [
          i.id,
          this.csvHucre(i.bolgeAdi),
          this.csvHucre(i.personelAdi ?? ''),
          this.csvHucre(i.personelSicilNo ?? ''),
          this.csvHucre(i.ihlalTipiAdi),
          this.csvHucre(i.tespitZamani),
          this.csvHucre(durumEtiketi(i.durum)),
        ].join(';')
      ),
    ];
    // Excel'in Türkçe karakterleri doğru açması için UTF-8 BOM + noktalı virgül
    const bom = '\uFEFF';
    const blob = new Blob([bom + csvSatirlari.join('\r\n')], {
      type: 'text/csv;charset=utf-8;',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const zaman = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
    a.href = url;
    a.download = `ihlal-kayitlari-${zaman}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  private csvHucre(deger: string | number): string {
    const metin = String(deger).replace(/"/g, '""');
    return `"${metin}"`;
  }

  cikisYap(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
