import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Ihlal, IhlalIstatistik, IhlalRedRequest } from '../models/ihlal.model';

/**
 * MODUL-2 (tasarim_mimari.md): /api/ihlaller uclarina karsilik gelen HTTP
 * cagrilari. Rol bazli kapsam (formen: kendi bolgesi + blurlu foto,
 * yonetici: tum fabrika + orijinal foto) tamamen backend'de (JWT'den
 * cozulen AuthenticatedUser) uygulanir; bu servis sadece cagriyi yapar.
 */
@Injectable({ providedIn: 'root' })
export class IhlalService {
  private readonly http = inject(HttpClient);

  /** apiUrl'den "/api" sonekini cikararak fotograflarin sunuldugu backend
   * origin'ini turetir (dev: http://localhost:8080, prod: bos = ayni origin). */
  private readonly fotoOrigin = environment.apiUrl.replace(/\/api\/?$/, '');

  listele(): Observable<Ihlal[]> {
    return this.http.get<Ihlal[]>(`${environment.apiUrl}/ihlaller`);
  }

  detay(id: number): Observable<Ihlal> {
    return this.http.get<Ihlal>(`${environment.apiUrl}/ihlaller/${id}`);
  }

  istatistik(): Observable<IhlalIstatistik[]> {
    return this.http.get<IhlalIstatistik[]>(`${environment.apiUrl}/ihlaller/istatistik`);
  }

  reddet(id: number, istek: IhlalRedRequest): Observable<Ihlal> {
    return this.http.post<Ihlal>(`${environment.apiUrl}/ihlaller/${id}/reddet`, istek);
  }

  /** Backend'in donduru "/uploads/..." bagil yolunu, JWT ile korunan
   * fotografi cekebilecegimiz tam URL'e cevirir (bkz. AuthImgDirective). */
  fotoTamUrl(fotoUrl: string): string {
    return `${this.fotoOrigin}${fotoUrl}`;
  }
}
