import { Component } from '@angular/core';
import { ExtranetHeader } from '../extranet-header/extranet-header';
import { ExtranetFooter } from '../extranet-footer/extranet-footer';

/**
 * Giriş ve ana sayfa için Erdemir Online kabuk düzeni.
 */
@Component({
  selector: 'app-extranet-shell',
  standalone: true,
  imports: [ExtranetHeader, ExtranetFooter],
  templateUrl: './extranet-shell.html',
  styleUrl: './extranet-shell.scss',
})
export class ExtranetShell {}
