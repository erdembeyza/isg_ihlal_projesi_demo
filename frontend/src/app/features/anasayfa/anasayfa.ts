import { Component } from '@angular/core';
import { ExtranetShell } from '../../shared/layout/extranet-shell/extranet-shell';

/**
 * Extranet ana sayfa bileşeni.
 * Erdemir Online açılış ekranını gösterir:
 * fabrika arka planı + alt hızlı erişim menüsü.
 */
@Component({
  selector: 'app-anasayfa',
  standalone: true,
  imports: [ExtranetShell],
  templateUrl: './anasayfa.html',
  styleUrl: './anasayfa.scss',
})
export class Anasayfa {}
