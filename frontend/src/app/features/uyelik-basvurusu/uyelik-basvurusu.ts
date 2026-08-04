import { Component } from '@angular/core';
import { ExtranetShell } from '../../shared/layout/extranet-shell/extranet-shell';

/**
 * Üyelik Başvurusu sayfası – ErdemirOnline'a yeni üyelik başvuru formu.
 */
@Component({
  selector: 'app-uyelik-basvurusu',
  standalone: true,
  imports: [ExtranetShell],
  templateUrl: './uyelik-basvurusu.html',
  styleUrl: './uyelik-basvurusu.scss',
})
export class UyelikBasvurusu {}
