import { Component, computed, input } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { KaliteIstatistik } from '../../../core/models/ihlal.model';

@Component({
  selector: 'app-kalite-grafik',
  standalone: true,
  imports: [BaseChartDirective],
  templateUrl: './kalite-grafik.html',
  styleUrl: './kalite-grafik.scss',
})
export class KaliteGrafikComponent {
  readonly kalite = input.required<KaliteIstatistik | null>();

  protected readonly chartData = computed<ChartConfiguration<'line'>['data']>(() => {
    const k = this.kalite();
    const trend = k?.haftalikTrend ?? [];
    return {
      labels: trend.map((t) => t.haftaEtiketi),
      datasets: [
        {
          data: trend.map((t) => t.fpOrani),
          label: 'FP oranı (%)',
          borderColor: '#b91c1c',
          backgroundColor: 'rgba(185, 28, 28, 0.15)',
          tension: 0.25,
          fill: true,
        },
      ],
    };
  });

  protected readonly chartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: '%' },
      },
    },
  };
}
