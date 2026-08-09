export type Rol = 'ISG_YONETICI' | 'FORMEN' | 'AI_CORE_SERVIS' | 'GORUNTULEYICI';

/** Backend: LoginRequestDTO */
export interface LoginRequest {
  kullaniciAdi: string;
  sifre: string;
}

/** Backend: LoginResponseDTO */
export interface LoginResponse {
  token: string;
  kullaniciId: number;
  kullaniciAdi: string;
  rol: Rol;
  adSoyad: string;
  bolgeId: number | null;
  bolgeIds?: number[];
}

/** Backend: ProfilResponseDTO */
export interface Profil {
  id: number;
  kullaniciAdi: string;
  adSoyad: string;
  rol: Rol;
  bolgeId: number | null;
  bolgeAdi: string | null;
  bolgeIds?: number[];
  aktifMi: boolean;
  eposta: string | null;
  telefon: string | null;
  gorev: string | null;
  sonGirisZamani: string | null;
}

export interface ProfilGuncelleRequest {
  adSoyad: string;
}

export interface SifreDegistirRequest {
  mevcutSifre: string;
  yeniSifre: string;
}

export function rolEtiketi(rol: Rol): string {
  switch (rol) {
    case 'ISG_YONETICI':
      return 'İSG Yöneticisi';
    case 'FORMEN':
      return 'Formen';
    case 'GORUNTULEYICI':
      return 'Görüntüleyici';
    case 'AI_CORE_SERVIS':
      return 'AI Core Servis';
  }
}
