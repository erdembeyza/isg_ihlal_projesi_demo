import { Component } from '@angular/core';
import { ExtranetShell } from '../../shared/layout/extranet-shell/extranet-shell';

/**
 * İletişim sayfası – Erdemir Online extranet iletişim bilgileri ve formu.
 */
@Component({
  selector: 'app-iletisim',
  standalone: true,
  imports: [ExtranetShell],
  templateUrl: './iletisim.html',
  styleUrl: './iletisim.scss',
})
export class Iletisim {}
