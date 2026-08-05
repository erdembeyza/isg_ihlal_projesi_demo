import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  KullaniciGuncelleRequest,
  KullaniciRequest,
  KullaniciResponse,
  SifreGuncelleRequest,
} from '../models/kullanici.model';

@Injectable({ providedIn: 'root' })
export class KullaniciService {
  private readonly http = inject(HttpClient);

  listele(): Observable<KullaniciResponse[]> {
    return this.http.get<KullaniciResponse[]>(`${environment.apiUrl}/kullanicilar`);
  }

  olustur(istek: KullaniciRequest): Observable<KullaniciResponse> {
    return this.http.post<KullaniciResponse>(`${environment.apiUrl}/kullanicilar`, istek);
  }

  guncelle(id: number, istek: KullaniciGuncelleRequest): Observable<KullaniciResponse> {
    return this.http.put<KullaniciResponse>(`${environment.apiUrl}/kullanicilar/${id}`, istek);
  }

  sifreGuncelle(id: number, istek: SifreGuncelleRequest): Observable<void> {
    return this.http.put<void>(`${environment.apiUrl}/kullanicilar/${id}/sifre`, istek);
  }
}
