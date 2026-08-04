export type Rol = 'ISG_YONETICI' | 'FORMEN' | 'AI_CORE_SERVIS';

/** Backend: LoginRequestDTO */
export interface LoginRequest {
  kullaniciAdi: string;
  sifre: string;
}

/** Backend: LoginResponseDTO */
export interface LoginResponse {
  token: string;
  rol: Rol;
  adSoyad: string;
  bolgeId: number | null;
}
