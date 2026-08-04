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
}

/** Backend: IhlalRedRequestDTO (ihlalId opsiyoneldir, asil id path'ten gelir) */
export interface IhlalRedRequest {
  ihlalId?: number;
  redNedeni: string | null;
}

/** Backend: IhlalIstatistikDTO */
export interface IhlalIstatistik {
  bolgeAdi: string;
  ihlalTipiAdi: string;
  toplamAdet: number;
  yuzdeDegisim: number;
}

/** Backend: PersonelIstatistikDTO */
export interface PersonelIstatistik {
  personelId: number;
  personelAdi: string;
  sicilNo: string;
  departman: string | null;
  toplamIhlal: number;
  enCokIhlalKategorisi: string;
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
