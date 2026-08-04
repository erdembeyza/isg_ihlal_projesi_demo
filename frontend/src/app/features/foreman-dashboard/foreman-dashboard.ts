import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { interval } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { IhlalService } from '../../core/services/ihlal.service';
import {
  Ihlal,
  IhlalIstatistik,
  PersonelIstatistik,
  durumEtiketi,
} from '../../core/models/ihlal.model';
import { IhlalListesiComponent } from '../../shared/components/ihlal-listesi/ihlal-listesi';
import { IstatistikGrafikComponent } from '../../shared/components/istatistik-grafik/istatistik-grafik';
import { IhlalDetayModalComponent } from '../../shared/components/ihlal-detay-modal/ihlal-detay-modal';

const TUMU = 'TÜMÜ';
const CANLI_YENILEME_MS = 5000;

type RiskDurumu = {
  etiket: string;
  seviye: 'stabil' | 'kritik';
};

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
  protected readonly personelIstatistikleri = signal<PersonelIstatistik[]>([]);
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
    this.ihlalService.personelIstatistik().subscribe({
      next: (veri) => this.personelIstatistikleri.set(veri),
    });
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
    this.aksiyonHatasi.set(null);
    this.cozuluyorId.set(ihlal.id);
    this.ihlalService.coz(ihlal.id).subscribe({
      next: (guncel) => {
        this.ihlaller.update((liste) => liste.map((i) => (i.id === guncel.id ? guncel : i)));
        if (this.secilenIhlal()?.id === guncel.id) {
          this.secilenIhlal.set(guncel);
        }
        this.cozuluyorId.set(null);
        this.ihlalService.personelIstatistik().subscribe({
          next: (veri) => this.personelIstatistikleri.set(veri),
        });
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
    this.router.navigate(['/giris']);
  }
}
