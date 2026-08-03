import { HttpClient } from '@angular/common/http';
import { Injectable, computed, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { LoginRequest, LoginResponse, Rol } from '../models/auth.model';

const STORAGE_KEY = 'isg_oturum';

/**
 * MODUL-3 (tasarim_mimari.md): giris/oturum yonetimi.
 * Basarili girişte backend'den donen LoginResponseDTO (token + rol + adSoyad +
 * bolgeId) tarayicida localStorage'a yazilir; sayfa yenilendiginde de oturum
 * buradan geri yuklenir (signal ile reaktif olarak uygulamaya yayilir).
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly oturum = signal<LoginResponse | null>(this.localStorageDanOku());

  readonly currentUser = this.oturum.asReadonly();
  readonly isLoggedIn = computed(() => this.oturum() !== null);
  readonly rol = computed<Rol | null>(() => this.oturum()?.rol ?? null);
  readonly isYonetici = computed(() => this.rol() === 'ISG_YONETICI');
  readonly isFormen = computed(() => this.rol() === 'FORMEN');

  constructor(private readonly http: HttpClient) {}

  login(istek: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login`, istek)
      .pipe(tap((yanit) => this.oturumuBaslat(yanit)));
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
