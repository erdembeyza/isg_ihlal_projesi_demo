export type IhlalDurumu = 'AKTIF' | 'HATALI_TESPIT';

/** Backend: IhlalResponseDTO */
export interface Ihlal {
  id: number;
  bolgeAdi: string;
  ihlalTipiAdi: string;
  tespitZamani: string;
  fotoUrl: string;
  durum: IhlalDurumu;
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
