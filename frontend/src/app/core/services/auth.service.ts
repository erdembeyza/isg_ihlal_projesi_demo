import { HttpClient } from '@angular/common/http';
import { Injectable, computed, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  LoginRequest,
  LoginResponse,
  Profil,
  ProfilGuncelleRequest,
  Rol,
  SifreDegistirRequest,
} from '../models/auth.model';

const STORAGE_KEY = 'isg_oturum';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly oturum = signal<LoginResponse | null>(this.localStorageDanOku());

  readonly currentUser = this.oturum.asReadonly();
  readonly isLoggedIn = computed(() => this.oturum() !== null);
  readonly rol = computed<Rol | null>(() => this.oturum()?.rol ?? null);
  readonly isYonetici = computed(() => this.rol() === 'ISG_YONETICI');
  readonly isFormen = computed(() => this.rol() === 'FORMEN');
  readonly isGoruntuleyici = computed(() => this.rol() === 'GORUNTULEYICI');

  constructor(private readonly http: HttpClient) {}

  login(istek: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login`, istek)
      .pipe(tap((yanit) => this.oturumuBaslat(yanit)));
  }

  profilGetir(): Observable<Profil> {
    return this.http.get<Profil>(`${environment.apiUrl}/auth/profil`);
  }

  profilGuncelle(istek: ProfilGuncelleRequest): Observable<Profil> {
    return this.http.put<Profil>(`${environment.apiUrl}/auth/profil`, istek).pipe(
      tap((profil) => this.oturumAdSoyadGuncelle(profil.adSoyad))
    );
  }

  sifreDegistir(istek: SifreDegistirRequest): Observable<void> {
    return this.http.put<void>(`${environment.apiUrl}/auth/sifre`, istek);
  }

  logout(): void {
    this.oturum.set(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  getToken(): string | null {
    return this.oturum()?.token ?? null;
  }

  private oturumuBaslat(yanit: LoginResponse): void {
    this.oturum.set(yanit);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(yanit));
  }

  private oturumAdSoyadGuncelle(adSoyad: string): void {
    const mevcut = this.oturum();
    if (!mevcut) {
      return;
    }
    const guncel = { ...mevcut, adSoyad };
    this.oturum.set(guncel);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(guncel));
  }

  private localStorageDanOku(): LoginResponse | null {
    const ham = localStorage.getItem(STORAGE_KEY);
    if (!ham) {
      return null;
    }
    try {
      return JSON.parse(ham) as LoginResponse;
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  }
}
