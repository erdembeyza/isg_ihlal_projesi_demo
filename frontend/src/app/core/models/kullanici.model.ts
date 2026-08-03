import { Rol } from './auth.model';

/** Backend: KullaniciRequestDTO */
export interface KullaniciRequest {
  kullaniciAdi: string;
  sifre: string;
  adSoyad: string;
  rol: Rol;
  bolgeId: number | null;
}

/** Backend: KullaniciResponseDTO */
export interface KullaniciResponse {
  id: number;
  kullaniciAdi: string;
  adSoyad: string;
  rol: Rol;
  bolgeId: number | null;
  aktifMi: boolean;
}
