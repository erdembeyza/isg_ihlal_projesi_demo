import { DecimalPipe } from '@angular/common';
import { Component, computed, input, output } from '@angular/core';
import { ChartConfiguration, ChartEvent } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { IhlalIstatistik } from '../../../core/models/ihlal.model';

const RENK_PALETI = ['#f6a821', '#1a4a6e', '#c0392b', '#1e7d3a', '#6b4fa0', '#0f2740'];

interface TrendSatiri {
  bolgeAdi: string;
  ihlalTipiAdi: string;
  toplamAdet: number;
  yuzdeDegisim: number;
  yuzdeMutlak: number;
}

/**
 * COMPONENT-5 (tasarim_mimari.md): Chart.js ile ihlal tiplerinin yuzdelik
 * dagilimini pasta grafik ile gosteren, rol bazli veri kapsamina duyarli
 * (input olarak zaten filtrelenmis veri alan) gorsellestirme bileseni.
 */
@Component({
  selector: 'app-istatistik-grafik',
  standalone: true,
  imports: [BaseChartDirective, DecimalPipe],
  templateUrl: './istatistik-grafik.html',
  styleUrl: './istatistik-grafik.scss',
})
export class IstatistikGrafikComponent {
  readonly istatistikler = input.required<IhlalIstatistik[]>();
  readonly tipSecildi = output<string>();

  protected readonly tipEtiketleri = computed(() => {
    const toplamlar = new Map<string, number>();
    for (const kayit of this.istatistikler()) {
      toplamlar.set(kayit.ihlalTipiAdi, (toplamlar.get(kayit.ihlalTipiAdi) ?? 0) + kayit.toplamAdet);
    }
    return [...toplamlar.entries()];
  });

  protected readonly chartData = computed<ChartConfiguration<'pie'>['data']>(() => {
    const girdiler = this.tipEtiketleri();
    return {
      labels: girdiler.map(([tip]) => tip),
      datasets: [
        {
          data: girdiler.map(([, adet]) => adet),
          backgroundColor: girdiler.map((_, i) => RENK_PALETI[i % RENK_PALETI.length]),
          borderWidth: 1,
        },
      ],
    };
  });

  protected readonly chartOptions: ChartConfiguration<'pie'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
    },
  };

  protected readonly toplamIhlalAdedi = computed(() =>
    this.tipEtiketleri().reduce((toplam, [, adet]) => toplam + adet, 0)
  );

  protected readonly trendSatirlari = computed<TrendSatiri[]>(() =>
    [...this.istatistikler()]
      .sort((a, b) => Math.abs(b.yuzdeDegisim) - Math.abs(a.yuzdeDegisim))
      .slice(0, 5)
      .map((kayit) => ({ ...kayit, yuzdeMutlak: Math.abs(kayit.yuzdeDegisim) }))
  );

  onChartClick(event: { event?: ChartEvent; active?: object[] }): void {
    const secilen = event.active?.[0] as { index?: number } | undefined;
    if (secilen?.index === undefined) {
      return;
    }
    const etiketler = this.chartData().labels as string[] | undefined;
    const tip = etiketler?.[secilen.index];
    if (tip) {
      this.tipSecildi.emit(tip);
    }
  }
}
