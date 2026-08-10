import { Component, computed, input } from '@angular/core';
import { PersonelIstatistik } from '../../../core/models/ihlal.model';

@Component({
  selector: 'app-personel-istatistik-paneli',
  standalone: true,
  templateUrl: './personel-istatistik-paneli.html',
  styleUrl: './personel-istatistik-paneli.scss',
})
export class PersonelIstatistikPaneliComponent {
  readonly kayitlar = input.required<PersonelIstatistik[]>();
  readonly limit = input(8);

  protected readonly gorunen = computed(() => this.kayitlar().slice(0, this.limit()));

  protected readonly enCok = computed(() => this.gorunen()[0] ?? null);

  protected readonly maxAdet = computed(() =>
    Math.max(1, ...this.gorunen().map((k) => k.toplamIhlal))
  );

  protected yuzde(adet: number): number {
    return Math.round((adet / this.maxAdet()) * 100);
  }

  protected tipOzeti(k: PersonelIstatistik): string {
    if (!k.tipDagilimi?.length) {
      return k.enCokIhlalKategorisi || '—';
    }
    return k.tipDagilimi.map((t) => `${t.tipAdi} (${t.adet})`).join(' · ');
  }
}
