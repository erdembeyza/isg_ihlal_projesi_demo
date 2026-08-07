import { Component, EventEmitter, Input, OnDestroy, Output, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { rolEtiketi } from '../../../core/models/auth.model';
import { KullaniciYonetimSayfasiComponent } from '../../components/kullanici-yonetim-sayfasi/kullanici-yonetim-sayfasi';
import { ProfilPaneliComponent } from '../../components/profil-paneli/profil-paneli';

@Component({
  selector: 'app-panel-shell',
  standalone: true,
  imports: [ProfilPaneliComponent, KullaniciYonetimSayfasiComponent],
  templateUrl: './panel-shell.html',
  styleUrl: './panel-shell.scss',
})
export class PanelShell implements OnDestroy {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  @Input() panelAdi = '';
  @Input() kullaniciAdi = '';
  @Input() rolAdi = '';
  @Input() cikisYap: (() => void) | null = null;
  @Output() cikis = new EventEmitter<void>();

  protected readonly profilAcik = signal(false);
  protected readonly kullaniciYonetimAcik = signal(false);

  readonly isYonetici = this.authService.isYonetici;

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

  readonly avatarHarf = computed(() => {
    const ad = this.kullaniciAdi || this.authService.currentUser()?.adSoyad || '?';
    return ad[0]?.toUpperCase() ?? '?';
  });

  readonly rolEtiketiMetni = computed(() => {
    const rol = this.authService.rol();
    return rol ? rolEtiketi(rol) : this.rolAdi;
  });

  constructor() {
    this.saatAraligi = setInterval(() => this.simdi.set(new Date()), 1000);
  }

  ngOnDestroy(): void {
    if (this.saatAraligi) clearInterval(this.saatAraligi);
  }

  profiliAc(): void {
    this.kullaniciYonetimAcik.set(false);
    this.profilAcik.set(true);
  }

  profiliKapat(): void {
    this.profilAcik.set(false);
  }

  kullaniciYonetiminiAc(): void {
    this.profilAcik.set(false);
    this.kullaniciYonetimAcik.set(true);
  }

  kullaniciYonetiminiKapat(): void {
    this.kullaniciYonetimAcik.set(false);
  }

  kullaniciYonetiminiToggle(): void {
    if (this.kullaniciYonetimAcik()) {
      this.kullaniciYonetiminiKapat();
    } else {
      this.kullaniciYonetiminiAc();
    }
  }

  onCikisYap(): void {
    this.profiliKapat();
    this.kullaniciYonetiminiKapat();
    this.cikis.emit();
    if (this.cikisYap) {
      this.cikisYap();
      return;
    }
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
