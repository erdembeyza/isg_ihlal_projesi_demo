import { sureMetni } from '../utils/sure-format';

export type IhlalDurumu = 'AKTIF' | 'HATALI_TESPIT' | 'COZULDU';

/** Backend: IhlalResponseDTO */
export interface Ihlal {
  id: number;
  bolgeAdi: string;
  ihlalTipiAdi: string;
  tespitZamani: string;
  fotoUrl: string;
  durum: IhlalDurumu;
  personelId: number | null;
  personelAdi: string | null;
  personelSicilNo: string | null;
  cozNotu: string | null;
  sureSaniye: number | null;
}

/** Backend: IhlalRedRequestDTO */
export interface IhlalRedRequest {
  ihlalId?: number;
  redNedeni: string | null;
}

/** Backend: IhlalCozRequestDTO */
export interface IhlalCozRequest {
  not?: string | null;
}

/** Backend: IhlalIstatistikDTO */
export interface IhlalIstatistik {
  bolgeAdi: string;
  ihlalTipiAdi: string;
  toplamAdet: number;
  yuzdeDegisim: number;
}

/** Backend: KameraDurumDTO */
export interface KameraDurum {
  id: number;
  bolgeId: number;
  bolgeAdi: string;
  kameraAdi: string;
  onlineMi: boolean;
  sonKareZamani: string | null;
  fps: number | null;
  guncellemeZamani: string;
}

/** Backend: IslemLogDTO */
export interface IslemLog {
  id: number;
  kullaniciId: number | null;
  kullaniciAdi: string;
  adSoyad: string;
  islemTipi: string;
  ilgiliIhlalId: number | null;
  islemZamani: string;
  detay: string | null;
}

/** Backend: KaliteIstatistikDTO */
export interface KaliteIstatistik {
  toplamIhlal: number;
  reddedilen: number;
  falsePositiveOrani: number;
  finetuneHavuzDosyaSayisi: number;
  haftalikTrend: HaftalikKaliteNoktasi[];
}

export interface HaftalikKaliteNoktasi {
  haftaEtiketi: string;
  toplam: number;
  reddedilen: number;
  fpOrani: number;
}

/** Backend: PersonelIstatistikDTO */
export interface PersonelIstatistik {
  personelId: number;
  personelAdi: string;
  sicilNo: string;
  departman: string | null;
  toplamIhlal: number;
  enCokIhlalKategorisi: string;
  tipDagilimi: { tipAdi: string; adet: number }[];
}

/** Backend: HaftalikRaporOzetDTO */
export interface HaftalikRaporOzet {
  baslangic: string;
  bitis: string;
  toplamIhlal: number;
  aktif: number;
  cozuldu: number;
  hataliTespit: number;
  bolgeOzetleri: { bolgeAdi: string; adet: number }[];
  tipOzetleri: { tipAdi: string; adet: number }[];
  riskliSaatler: { saat: number; adet: number }[];
}

export function durumEtiketi(durum: IhlalDurumu): string {
  switch (durum) {
    case 'AKTIF':
      return 'Aktif';
    case 'COZULDU':
      return 'Çözüldü';
    case 'HATALI_TESPIT':
      return 'Hatalı Tespit';
  }
}

/** Panelde gorunen acik sure: AKTIF iken canli, kapaninca backend'deki sureSaniye. */
export function ihlalAcikSureSaniye(ihlal: Ihlal, simdi = new Date()): number {
  if (ihlal.durum !== 'AKTIF' && ihlal.sureSaniye != null) {
    return ihlal.sureSaniye;
  }
  const baslangic = new Date(ihlal.tespitZamani).getTime();
  if (Number.isNaN(baslangic)) {
    return ihlal.sureSaniye ?? 0;
  }
  return Math.max(0, Math.floor((simdi.getTime() - baslangic) / 1000));
}

export function ihlalAcikSureMetni(ihlal: Ihlal, simdi = new Date()): string {
  return sureMetni(ihlalAcikSureSaniye(ihlal, simdi));
}
