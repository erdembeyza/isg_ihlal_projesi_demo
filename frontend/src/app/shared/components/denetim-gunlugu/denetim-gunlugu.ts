import { DatePipe } from '@angular/common';

import { Component, computed, input, signal } from '@angular/core';

import { IslemLog } from '../../../core/models/ihlal.model';



type FiltreTipi = 'TUMU' | 'GIRIS' | 'GIRIS_BASARISIZ' | 'IHLAL_COZME' | 'IHLAL_REDDETME' | 'DIGER';



const TIP_ETIKETLERI: Record<string, string> = {

  GIRIS: 'Giriş',

  GIRIS_BASARISIZ: 'Hatalı giriş',

  IHLAL_COZME: 'Çözüldü',

  IHLAL_REDDETME: 'Reddetme',

  KULLANICI_GUNCELLEME: 'Kullanıcı güncelleme',

  SIFRE_GUNCELLEME: 'Parola güncelleme',

  PROFIL_GUNCELLEME: 'Profil güncelleme',

  SIFRE_DEGISTIRME: 'Parola değiştirme',

};



const DETAY_ETIKETLERI: Record<string, string> = {

  'Yanlis parola': 'Yanlış parola',

  'Hatali parola': 'Yanlış parola',

  'Bilinmeyen kullanici adi': 'Bilinmeyen kullanıcı adı',

  'Pasif hesap': 'Pasif hesap',

  'Basarili giris': 'Başarılı giriş',

};



@Component({

  selector: 'app-denetim-gunlugu',

  standalone: true,

  imports: [DatePipe],

  templateUrl: './denetim-gunlugu.html',

  styleUrl: './denetim-gunlugu.scss',

})

export class DenetimGunluguComponent {

  readonly loglar = input.required<IslemLog[]>();



  protected readonly filtre = signal<FiltreTipi>('TUMU');



  protected readonly filtreSecenekleri = computed(() => {

    const sayilar = { GIRIS: 0, GIRIS_BASARISIZ: 0, IHLAL_COZME: 0, IHLAL_REDDETME: 0, DIGER: 0 };

    for (const log of this.loglar()) {

      if (log.islemTipi === 'GIRIS') sayilar.GIRIS++;

      else if (log.islemTipi === 'GIRIS_BASARISIZ') sayilar.GIRIS_BASARISIZ++;

      else if (log.islemTipi === 'IHLAL_COZME') sayilar.IHLAL_COZME++;

      else if (log.islemTipi === 'IHLAL_REDDETME') sayilar.IHLAL_REDDETME++;

      else sayilar.DIGER++;

    }

    return [

      { tip: 'TUMU' as const, etiket: 'Tümü', adet: this.loglar().length },

      { tip: 'GIRIS_BASARISIZ' as const, etiket: 'Hatalı giriş', adet: sayilar.GIRIS_BASARISIZ },

      { tip: 'GIRIS' as const, etiket: 'Başarılı giriş', adet: sayilar.GIRIS },

      { tip: 'IHLAL_COZME' as const, etiket: 'Çözüldü', adet: sayilar.IHLAL_COZME },

      { tip: 'IHLAL_REDDETME' as const, etiket: 'Reddetme', adet: sayilar.IHLAL_REDDETME },

      ...(sayilar.DIGER > 0

        ? [{ tip: 'DIGER' as const, etiket: 'Diğer', adet: sayilar.DIGER }]

        : []),

    ];

  });



  protected readonly filtreliLoglar = computed(() => {

    const f = this.filtre();

    if (f === 'TUMU') return this.loglar();

    if (f === 'DIGER') {

      return this.loglar().filter(

        (l) => !['GIRIS', 'GIRIS_BASARISIZ', 'IHLAL_COZME', 'IHLAL_REDDETME'].includes(l.islemTipi)

      );

    }

    return this.loglar().filter((l) => l.islemTipi === f);

  });



  tipEtiketi(tip: string): string {

    return TIP_ETIKETLERI[tip] ?? tip;

  }



  detayMetni(detay: string | null): string {

    if (!detay) return '—';

    return DETAY_ETIKETLERI[detay] ?? detay;

  }



  tipSinifi(tip: string): string {

    switch (tip) {

      case 'GIRIS':

        return 'giris';

      case 'GIRIS_BASARISIZ':

        return 'giris-hatali';

      case 'IHLAL_COZME':

        return 'cozme';

      case 'IHLAL_REDDETME':

        return 'reddetme';

      default:

        return 'diger';

    }

  }



  satirSinifi(tip: string): string {

    return tip === 'GIRIS_BASARISIZ' ? 'hatali-giris-satiri' : '';

  }



  filtreSec(tip: FiltreTipi): void {

    this.filtre.set(tip);

  }

}

