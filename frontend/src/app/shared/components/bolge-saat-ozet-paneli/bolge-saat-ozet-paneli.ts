import { Component, computed, input } from '@angular/core';
import { HaftalikRaporOzet } from '../../../core/models/ihlal.model';

@Component({
  selector: 'app-bolge-saat-ozet-paneli',
  standalone: true,
  templateUrl: './bolge-saat-ozet-paneli.html',
  styleUrl: './bolge-saat-ozet-paneli.scss',
})
export class BolgeSaatOzetPaneliComponent {
  readonly rapor = input.required<HaftalikRaporOzet | null>();

  protected readonly bolgeler = computed(() => this.rapor()?.bolgeOzetleri ?? []);
  protected readonly tipler = computed(() => this.rapor()?.tipOzetleri ?? []);
  protected readonly saatler = computed(() => this.rapor()?.riskliSaatler ?? []);

  protected readonly enRiskliBolge = computed(() => this.bolgeler()[0] ?? null);
  protected readonly enRiskliSaat = computed(() => this.saatler()[0] ?? null);

  protected readonly maxBolge = computed(() =>
    Math.max(1, ...this.bolgeler().map((b) => b.adet))
  );
  protected readonly maxSaat = computed(() =>
    Math.max(1, ...this.saatler().map((s) => s.adet))
  );

  protected saatEtiket(saat: number): string {
    return `${String(saat).padStart(2, '0')}:00`;
  }

  protected yuzde(adet: number, max: number): number {
    return Math.round((adet / max) * 100);
  }
}
