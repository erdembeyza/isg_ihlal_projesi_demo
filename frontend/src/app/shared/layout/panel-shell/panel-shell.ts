import { Component } from '@angular/core';
import { ExtranetHeader } from '../extranet-header/extranet-header';
import { ExtranetFooter } from '../extranet-footer/extranet-footer';

/**
 * Panel sayfaları için üst menü + içerik kabuğu.
 */
@Component({
  selector: 'app-panel-shell',
  standalone: true,
  imports: [ExtranetHeader, ExtranetFooter],
  templateUrl: './panel-shell.html',
  styleUrl: './panel-shell.scss',
})
export class PanelShell {}
