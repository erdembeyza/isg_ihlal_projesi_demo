import { NgTemplateOutlet } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, effect, inject, input, OnInit, output, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { rolEtiketi, Rol } from '../../../core/models/auth.model';
import { Bolge } from '../../../core/models/bolge.model';
import { KullaniciResponse } from '../../../core/models/kullanici.model';
import { BolgeService } from '../../../core/services/bolge.service';
import { KullaniciService } from '../../../core/services/kullanici.service';

type KullaniciGrupRol = 'FORMEN' | 'ISG_YONETICI' | 'GORUNTULEYICI';

interface KullaniciGrup {
  rol: KullaniciGrupRol;
  etiket: string;
  aciklama: string;
  liste: KullaniciResponse[];
}

@Component({
  selector: 'app-kullanici-yonetim-sayfasi',
  standalone: true,
  imports: [ReactiveFormsModule, NgTemplateOutlet],
  templateUrl: './kullanici-yonetim-sayfasi.html',
  styleUrl: './kullanici-yonetim-sayfasi.scss',
})
export class KullaniciYonetimSayfasiComponent implements OnInit {
  private readonly kullaniciService = inject(KullaniciService);
  private readonly bolgeService = inject(BolgeService);
  private readonly fb = inject(FormBuilder);

  readonly acik = input(false);
  readonly kapandi = output<void>();

  protected readonly rolEtiketi = rolEtiketi;

  protected readonly kullanicilar = signal<KullaniciResponse[]>([]);
  protected readonly bolgeler = signal<Bolge[]>([]);
  protected readonly yukleniyor = signal(false);
  protected readonly mesaj = signal<{ tur: 'basari' | 'hata'; metin: string } | null>(null);
  protected readonly duzenlenenId = signal<number | null>(null);
  protected readonly kaydediliyor = signal(false);
  protected readonly acikGruplar = signal<Record<KullaniciGrupRol, boolean>>({
    FORMEN: true,
    ISG_YONETICI: false,
    GORUNTULEYICI: false,
  });

  protected readonly formenler = computed(() =>
    this.kullanicilar().filter((k) => k.rol === 'FORMEN')
  );
  protected readonly yoneticiler = computed(() =>
    this.kullanicilar().filter((k) => k.rol === 'ISG_YONETICI')
  );
  protected readonly izleyiciler = computed(() =>
    this.kullanicilar().filter((k) => k.rol === 'GORUNTULEYICI')
  );
  protected readonly kullaniciGruplari = computed((): KullaniciGrup[] => [
    {
      rol: 'FORMEN',
      etiket: 'Formenler',
      aciklama: 'Bölgeye bağlı saha sorumluları',
      liste: this.formenler(),
    },
    {
      rol: 'ISG_YONETICI',
      etiket: 'Yöneticiler',
      aciklama: 'Tam yetkili ISG yöneticileri',
      liste: this.yoneticiler(),
    },
    {
      rol: 'GORUNTULEYICI',
      etiket: 'İzleyiciler',
      aciklama: 'Salt okunur üst yönetim hesapları',
      liste: this.izleyiciler(),
    },
  ]);

  protected readonly yeniKullaniciForm = this.fb.nonNullable.group({
    kullaniciAdi: ['', [Validators.required, Validators.minLength(3)]],
    sifre: ['', [Validators.required, Validators.minLength(6)]],
    adSoyad: ['', [Validators.required]],
    rol: ['FORMEN' as Rol, [Validators.required]],
    bolgeIds: [[] as number[]],
  });

  protected readonly duzenleForm = this.fb.nonNullable.group({
    kullaniciAdi: ['', [Validators.required, Validators.minLength(3)]],
    adSoyad: ['', [Validators.required]],
    rol: ['FORMEN' as Rol, [Validators.required]],
    bolgeIds: [[] as number[]],
    aktifMi: [true],
    yeniSifre: [''],
    eposta: [''],
    telefon: [''],
    gorev: [''],
  });

  constructor() {
    effect(() => {
      if (this.acik()) {
        this.verileriYukle();
      } else {
        this.temizle();
      }
    });
  }

  ngOnInit(): void {
    this.bolgeService.listele().subscribe({ next: (b) => this.bolgeler.set(b) });
  }

  arkaPlanaTiklandi(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.kapat();
    }
  }

  kapat(): void {
    this.kapandi.emit();
  }

  kullanicilariYenile(): void {
    this.kullanicilariYukle();
  }

  yeniKullaniciOlustur(): void {
    if (this.yeniKullaniciForm.invalid) {
      this.yeniKullaniciForm.markAllAsTouched();
      return;
    }
    const deger = this.yeniKullaniciForm.getRawValue();
    const bolgeIds = this.bolgeIdsCozumle(deger.rol, deger.bolgeIds);
    if (deger.rol === 'FORMEN' && bolgeIds.length === 0) {
      this.mesaj.set({ tur: 'hata', metin: 'Formen rolü için en az bir bölge seçimi zorunludur.' });
      return;
    }
    this.kaydediliyor.set(true);
    this.mesaj.set(null);
    this.kullaniciService
      .olustur({
        kullaniciAdi: deger.kullaniciAdi,
        sifre: deger.sifre,
        adSoyad: deger.adSoyad,
        rol: deger.rol,
        bolgeId: deger.rol === 'FORMEN' ? bolgeIds[0] : null,
        bolgeIds: deger.rol === 'FORMEN' ? bolgeIds : null,
      })
      .subscribe({
        next: (yanit) => {
          this.kaydediliyor.set(false);
          this.mesaj.set({ tur: 'basari', metin: `"${yanit.kullaniciAdi}" kullanıcısı oluşturuldu.` });
          this.yeniKullaniciForm.reset({ kullaniciAdi: '', sifre: '', adSoyad: '', rol: 'FORMEN', bolgeIds: [] });
          this.kullanicilariYukle();
        },
        error: (hata: HttpErrorResponse) => {
          this.kaydediliyor.set(false);
          this.mesaj.set({
            tur: 'hata',
            metin: hata.status === 409 ? 'Bu kullanıcı adı zaten kayıtlı.' : 'Kullanıcı oluşturulamadı.',
          });
        },
      });
  }

  grupToggle(rol: KullaniciGrupRol): void {
    this.acikGruplar.update((mevcut) => ({ ...mevcut, [rol]: !mevcut[rol] }));
  }

  grupAcikMi(rol: KullaniciGrupRol): boolean {
    return this.acikGruplar()[rol];
  }

  duzenlemeyiAc(kullanici: KullaniciResponse): void {
    this.duzenlenenId.set(kullanici.id);
    const bolgeIds =
      kullanici.bolgeIds && kullanici.bolgeIds.length > 0
        ? [...kullanici.bolgeIds]
        : kullanici.bolgeId != null
          ? [kullanici.bolgeId]
          : [];
    this.duzenleForm.setValue({
      kullaniciAdi: kullanici.kullaniciAdi,
      adSoyad: kullanici.adSoyad,
      rol: kullanici.rol,
      bolgeIds,
      aktifMi: kullanici.aktifMi,
      yeniSifre: '',
      eposta: kullanici.eposta ?? '',
      telefon: kullanici.telefon ?? '',
      gorev: kullanici.gorev ?? '',
    });
    this.mesaj.set(null);
  }

  duzenlemeyiIptal(): void {
    this.duzenlenenId.set(null);
  }

  kullaniciKaydet(id: number): void {
    if (this.duzenleForm.invalid) {
      this.duzenleForm.markAllAsTouched();
      return;
    }
    const deger = this.duzenleForm.getRawValue();
    const bolgeIds = this.bolgeIdsCozumle(deger.rol, deger.bolgeIds);
    if (deger.rol === 'FORMEN' && bolgeIds.length === 0) {
      this.mesaj.set({ tur: 'hata', metin: 'Formen rolü için en az bir bölge seçimi zorunludur.' });
      return;
    }
    const yeniSifre = deger.yeniSifre.trim();
    if (yeniSifre && yeniSifre.length < 6) {
      this.mesaj.set({ tur: 'hata', metin: 'Yeni parola en az 6 karakter olmalıdır.' });
      return;
    }
    this.kaydediliyor.set(true);
    this.mesaj.set(null);
    this.kullaniciService
      .guncelle(id, {
        kullaniciAdi: deger.kullaniciAdi.trim(),
        adSoyad: deger.adSoyad,
        rol: deger.rol,
        bolgeId: deger.rol === 'FORMEN' ? bolgeIds[0] : null,
        bolgeIds: deger.rol === 'FORMEN' ? bolgeIds : null,
        aktifMi: deger.aktifMi,
        yeniSifre: yeniSifre || null,
        eposta: deger.eposta.trim() || null,
        telefon: deger.telefon.trim() || null,
        gorev: deger.gorev.trim() || null,
      })
      .subscribe({
        next: () => {
          this.kaydediliyor.set(false);
          this.duzenlenenId.set(null);
          this.mesaj.set({ tur: 'basari', metin: 'Kullanıcı bilgileri güncellendi.' });
          this.kullanicilariYukle();
        },
        error: (hata: HttpErrorResponse) => {
          this.kaydediliyor.set(false);
          this.mesaj.set({
            tur: 'hata',
            metin: hata.error?.hata ?? 'Kullanıcı güncellenemedi.',
          });
        },
      });
  }

  private verileriYukle(): void {
    this.kullanicilariYukle();
  }

  private kullanicilariYukle(): void {
    this.yukleniyor.set(true);
    this.mesaj.set(null);
    this.kullaniciService.listele().subscribe({
      next: (liste) => {
        this.kullanicilar.set(liste);
        this.yukleniyor.set(false);
      },
      error: () => {
        this.yukleniyor.set(false);
        this.mesaj.set({
          tur: 'hata',
          metin: 'Kayıtlı kullanıcılar veritabanından alınamadı. Backend çalışıyor mu kontrol edin.',
        });
      },
    });
  }

  private temizle(): void {
    this.duzenlenenId.set(null);
    this.mesaj.set(null);
    this.duzenleForm.reset();
    this.acikGruplar.set({
      FORMEN: true,
      ISG_YONETICI: false,
      GORUNTULEYICI: false,
    });
  }

  private bolgeIdsCozumle(rol: Rol, bolgeIds: number[] | (string | number)[] | null | undefined): number[] {
    if (rol !== 'FORMEN' || !bolgeIds?.length) {
      return [];
    }
    return bolgeIds
      .map((v) => Number(v))
      .filter((n) => !Number.isNaN(n));
  }
}
