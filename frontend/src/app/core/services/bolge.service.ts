import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Bolge } from '../models/bolge.model';

/**
 * GET /api/bolgeler: tanimli tum uretim bolgelerini getirir (dropdown/filtre
 * gibi kullanimlar icin). Hem ISG_YONETICI hem FORMEN erisebilir.
 */
@Injectable({ providedIn: 'root' })
export class BolgeService {
  private readonly http = inject(HttpClient);

  listele(): Observable<Bolge[]> {
    return this.http.get<Bolge[]>(`${environment.apiUrl}/bolgeler`);
  }
}
