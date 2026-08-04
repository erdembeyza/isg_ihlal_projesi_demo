import { Component, OnDestroy, computed, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

/**
 * Erdemir Online extranet üst menü ve marka alanı.
 * Giriş/ana sayfa ile panel sayfalarında ortak kullanılır.
 */
@Component({
  selector: 'app-extranet-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './extranet-header.html',
  styleUrl: './extranet-header.scss',
})
export class ExtranetHeader implements OnDestroy {
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
    if (this.saatAraligi) {
      clearInterval(this.saatAraligi);
    }
  }
}
