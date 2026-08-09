import { DatePipe } from '@angular/common';
import { Component, computed, inject, input, OnDestroy, OnInit, output, signal } from '@angular/core';
import { IhlalService } from '../../../core/services/ihlal.service';
import { Ihlal, durumEtiketi, ihlalAcikSureMetni } from '../../../core/models/ihlal.model';
import { AuthImgDirective } from '../../../core/directives/auth-img.directive';

type SiralamaAlani = 'tespitZamani' | 'bolgeAdi' | 'ihlalTipiAdi';

const SAYFA_BOYUTU = 8;

/**
 * COMPONENT-4 (tasarim_mimari.md): ihlal kayitlarini tablo halinde listeleyen,
 * hem yonetici hem formen panelinde ortak kullanilan (shared) bilesen.
 * Filtreleme sorumlulugu ust bilesenlerde (dashboard'lar); bu bilesen sadece
 * kendisine gelen listeyi siralar/sayfalar ve satir tiklamasini disari bildirir.
 */
@Component({
  selector: 'app-ihlal-listesi',
  standalone: true,
  imports: [AuthImgDirective, DatePipe],
  templateUrl: './ihlal-listesi.html',
  styleUrl: './ihlal-listesi.scss',
})
export class IhlalListesiComponent implements OnInit, OnDestroy {
  protected readonly ihlalService = inject(IhlalService);
  protected readonly durumEtiketi = durumEtiketi;
  protected readonly ihlalAcikSureMetni = ihlalAcikSureMetni;

  readonly ihlaller = input.required<Ihlal[]>();
  /** Formen panelinde AKTIF ihlaller icin "Cozuldu Isaretle" butonu gosterilir. */
  readonly cozulebilirMi = input(false);
  readonly cozuluyorId = input<number | null>(null);
  readonly satirSecildi = output<Ihlal>();
  readonly cozuldu = output<Ihlal>();

  protected readonly simdi = signal(new Date());
  private saatAraligi?: ReturnType<typeof setInterval>;

  protected readonly sayfa = signal(0);
  protected readonly siralamaAlani = signal<SiralamaAlani>('tespitZamani');
  protected readonly siralamaYonu = signal<'asc' | 'desc'>('desc');

  protected readonly sirali = computed(() => {
    const alan = this.siralamaAlani();
    const yon = this.siralamaYonu() === 'asc' ? 1 : -1;
    return [...this.ihlaller()].sort((a, b) => {
      const aDeger = a[alan] ?? '';
      const bDeger = b[alan] ?? '';
      if (aDeger < bDeger) return -1 * yon;
      if (aDeger > bDeger) return 1 * yon;
      return 0;
    });
  });

  protected readonly toplamSayfa = computed(() =>
    Math.max(1, Math.ceil(this.sirali().length / SAYFA_BOYUTU))
  );

  protected readonly gecerliSayfa = computed(() => Math.min(this.sayfa(), this.toplamSayfa() - 1));

  protected readonly gorunenSatirlar = computed(() => {
    const baslangic = this.gecerliSayfa() * SAYFA_BOYUTU;
    return this.sirali().slice(baslangic, baslangic + SAYFA_BOYUTU);
  });

  ngOnInit(): void {
    this.saatAraligi = setInterval(() => this.simdi.set(new Date()), 1000);
  }

  ngOnDestroy(): void {
    if (this.saatAraligi) {
      clearInterval(this.saatAraligi);
    }
  }

  acikSure(ihlal: Ihlal): string {
    this.simdi();
    return ihlalAcikSureMetni(ihlal, this.simdi());
  }

  siralaAlaninaGore(alan: SiralamaAlani): void {
    if (this.siralamaAlani() === alan) {
      this.siralamaYonu.set(this.siralamaYonu() === 'asc' ? 'desc' : 'asc');
    } else {
      this.siralamaAlani.set(alan);
      this.siralamaYonu.set('desc');
    }
    this.sayfa.set(0);
  }

  oncekiSayfa(): void {
    this.sayfa.set(Math.max(0, this.gecerliSayfa() - 1));
  }

  sonrakiSayfa(): void {
    this.sayfa.set(Math.min(this.toplamSayfa() - 1, this.gecerliSayfa() + 1));
  }

  cozTiklandi(event: MouseEvent, ihlal: Ihlal): void {
    event.stopPropagation();
    if (ihlal.durum !== 'AKTIF' || this.cozuluyorId() === ihlal.id) {
      return;
    }
    this.cozuldu.emit(ihlal);
  }
}
