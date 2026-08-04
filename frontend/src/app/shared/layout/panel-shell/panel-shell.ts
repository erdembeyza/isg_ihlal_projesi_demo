import { Component, EventEmitter, Input, OnDestroy, Output, computed, signal } from '@angular/core';
import { ExtranetFooter } from '../extranet-footer/extranet-footer';

/**
 * Panel sayfaları için tek parça birleşik header + içerik kabuğu.
 * ExtranetHeader ve panel-basligi birleştirildi.
 */
@Component({
  selector: 'app-panel-shell',
  standalone: true,
  imports: [ExtranetFooter],
  templateUrl: './panel-shell.html',
  styleUrl: './panel-shell.scss',
})
export class PanelShell implements OnDestroy {
  @Input() panelAdi = '';
  @Input() kullaniciAdi = '';
  @Input() rolAdi = '';
  @Input() cikisYap: (() => void) | null = null;
  @Output() cikis = new EventEmitter<void>();

  private saatAraligi?: ReturnType<typeof setInterval>;

  readonly simdi = signal(new Date());

  readonly tarihSaatMetni = computed(() => {
    const tarih = this.simdi();
    return tarih.toLocaleString('tr-TR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      weekday: 'long',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  });

  constructor() {
    this.saatAraligi = setInterval(() => this.simdi.set(new Date()), 1000);
  }

  ngOnDestroy(): void {
    if (this.saatAraligi) clearInterval(this.saatAraligi);
  }

  onCikisYap(): void {
    this.cikis.emit();
    if (this.cikisYap) this.cikisYap();
  }
}
