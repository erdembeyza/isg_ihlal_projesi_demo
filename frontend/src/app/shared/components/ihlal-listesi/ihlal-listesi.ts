import { DatePipe } from '@angular/common';
import { Component, computed, inject, input, output, signal } from '@angular/core';
import { IhlalService } from '../../../core/services/ihlal.service';
import { Ihlal } from '../../../core/models/ihlal.model';
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
export class IhlalListesiComponent {
  protected readonly ihlalService = inject(IhlalService);

  readonly ihlaller = input.required<Ihlal[]>();
  readonly satirSecildi = output<Ihlal>();

  protected readonly sayfa = signal(0);
  protected readonly siralamaAlani = signal<SiralamaAlani>('tespitZamani');
  protected readonly siralamaYonu = signal<'asc' | 'desc'>('desc');

  protected readonly sirali = computed(() => {
    const alan = this.siralamaAlani();
    const yon = this.siralamaYonu() === 'asc' ? 1 : -1;
    return [...this.ihlaller()].sort((a, b) => {
      if (a[alan] < b[alan]) return -1 * yon;
      if (a[alan] > b[alan]) return 1 * yon;
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
}
