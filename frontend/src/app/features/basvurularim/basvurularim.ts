import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ExtranetShell } from '../../shared/layout/extranet-shell/extranet-shell';

/**
 * Başvurularım sayfası – kullanıcının üyelik başvurularını sorgulayıp görüntüler.
 */
@Component({
  selector: 'app-basvurularim',
  standalone: true,
  imports: [ExtranetShell, RouterLink],
  templateUrl: './basvurularim.html',
  styleUrl: './basvurularim.scss',
})
export class Basvurularim {}
