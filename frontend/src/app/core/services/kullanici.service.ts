import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { KullaniciRequest, KullaniciResponse } from '../models/kullanici.model';

/**
 * POST /api/kullanicilar: yeni formen/kullanici tanimlar. Yalnizca
 * ISG_YONETICI rolu yetkilidir (backend @PreAuthorize ile korur).
 */
@Injectable({ providedIn: 'root' })
export class KullaniciService {
  private readonly http = inject(HttpClient);

  olustur(istek: KullaniciRequest): Observable<KullaniciResponse> {
    return this.http.post<KullaniciResponse>(`${environment.apiUrl}/kullanicilar`, istek);
  }
}
