import { DatePipe } from '@angular/common';
import { Component, input } from '@angular/core';
import { KameraDurum } from '../../../core/models/ihlal.model';

@Component({
  selector: 'app-kamera-durum-paneli',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './kamera-durum-paneli.html',
  styleUrl: './kamera-durum-paneli.scss',
})
export class KameraDurumPaneliComponent {
  readonly kameralar = input.required<KameraDurum[]>();
}
