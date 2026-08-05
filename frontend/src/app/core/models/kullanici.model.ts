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
  bolgeAdi: string | null;
  aktifMi: boolean;
  eposta: string | null;
  telefon: string | null;
  gorev: string | null;
}

export interface KullaniciGuncelleRequest {
  kullaniciAdi: string;
  adSoyad: string;
  rol: Rol;
  bolgeId: number | null;
  aktifMi: boolean;
  yeniSifre?: string | null;
  eposta?: string | null;
  telefon?: string | null;
  gorev?: string | null;
}

export interface SifreGuncelleRequest {
  yeniSifre: string;
}
