import { DatePipe } from '@angular/common';
import { Component, inject, input, output, signal } from '@angular/core';
import { AuthImgDirective } from '../../../core/directives/auth-img.directive';
import { IhlalService } from '../../../core/services/ihlal.service';
import { Ihlal } from '../../../core/models/ihlal.model';

/**
 * COMPONENT-6 (tasarim_mimari.md): secilen ihlalin fotografini (role gore
 * orijinal/blurlu, AuthImgDirective ile), tespit zamanini ve bolgesini
 * buyuk gorunumde sunan; yoneticiler icin "Reddet" aksiyonunu barindiran
 * modal bilesen. API cagrisini (reddet) yapmaz; sadece disariya bildirir,
 * gercek istek ve liste yenilemesi ust dashboard bilesenine aittir.
 */
@Component({
  selector: 'app-ihlal-detay-modal',
  standalone: true,
  imports: [AuthImgDirective, DatePipe],
  templateUrl: './ihlal-detay-modal.html',
  styleUrl: './ihlal-detay-modal.scss',
})
export class IhlalDetayModalComponent {
  protected readonly ihlalService = inject(IhlalService);

  readonly ihlal = input.required<Ihlal | null>();
  readonly yetkiliMi = input<boolean>(false);
  readonly gonderiliyor = input<boolean>(false);

  readonly kapat = output<void>();
  readonly reddet = output<{ id: number; redNedeni: string | null }>();

  protected readonly redFormuAcik = signal(false);
  protected readonly redNedeni = signal('');

  redFormunuAc(): void {
    this.redFormuAcik.set(true);
  }

  redFormunuIptalEt(): void {
    this.redFormuAcik.set(false);
    this.redNedeni.set('');
  }

  redOnayla(): void {
    const mevcutIhlal = this.ihlal();
    if (!mevcutIhlal) {
      return;
    }
    this.reddet.emit({ id: mevcutIhlal.id, redNedeni: this.redNedeni().trim() || null });
  }

  arkaPlanaTiklandi(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.kapat.emit();
    }
  }
}
