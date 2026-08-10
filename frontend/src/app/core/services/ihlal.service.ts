import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  HaftalikRaporOzet,
  Ihlal,
  IhlalCozRequest,
  IhlalIstatistik,
  IhlalRedRequest,
  IslemLog,
  KaliteIstatistik,
  KameraDurum,
  PersonelIstatistik,
} from '../models/ihlal.model';

@Injectable({ providedIn: 'root' })
export class IhlalService {
  private readonly http = inject(HttpClient);

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

  personelIstatistik(): Observable<PersonelIstatistik[]> {
    return this.http.get<PersonelIstatistik[]>(`${environment.apiUrl}/ihlaller/istatistik/personel`);
  }

  kaliteIstatistik(): Observable<KaliteIstatistik> {
    return this.http.get<KaliteIstatistik>(`${environment.apiUrl}/ihlaller/istatistik/kalite`);
  }

  reddet(id: number, istek: IhlalRedRequest): Observable<Ihlal> {
    return this.http.post<Ihlal>(`${environment.apiUrl}/ihlaller/${id}/reddet`, istek);
  }

  coz(id: number, istek: IhlalCozRequest = {}): Observable<Ihlal> {
    return this.http.post<Ihlal>(`${environment.apiUrl}/ihlaller/${id}/coz`, istek);
  }

  kameraDurumlari(): Observable<KameraDurum[]> {
    return this.http.get<KameraDurum[]>(`${environment.apiUrl}/kameralar/durum`);
  }

  islemLoglari(limit = 100, tip?: string): Observable<IslemLog[]> {
    let params = new HttpParams().set('limit', limit);
    if (tip) {
      params = params.set('tip', tip);
    }
    return this.http.get<IslemLog[]>(`${environment.apiUrl}/islem-loglari`, { params });
  }

  haftalikRaporOzet(baslangic?: string, bitis?: string): Observable<HaftalikRaporOzet> {
    let params = new HttpParams();
    if (baslangic) params = params.set('baslangic', baslangic);
    if (bitis) params = params.set('bitis', bitis);
    return this.http.get<HaftalikRaporOzet>(`${environment.apiUrl}/raporlar/haftalik`, { params });
  }

  /** PDF blob indirmek icin (JWT Authorization header ile). */
  haftalikRaporPdf(baslangic?: string, bitis?: string): Observable<Blob> {
    let params = new HttpParams();
    if (baslangic) params = params.set('baslangic', baslangic);
    if (bitis) params = params.set('bitis', bitis);
    return this.http.get(`${environment.apiUrl}/raporlar/haftalik.pdf`, {
      params,
      responseType: 'blob',
    });
  }

  finetuneSenkronize(): Observable<{ toplam: number; kopyalanan: number; atlanan: number; hata: number }> {
    return this.http.post<{ toplam: number; kopyalanan: number; atlanan: number; hata: number }>(
      `${environment.apiUrl}/ihlaller/finetune-havuz/senkronize`,
      {}
    );
  }

  fotoTamUrl(fotoUrl: string): string {
    return `${this.fotoOrigin}${fotoUrl}`;
  }
}
