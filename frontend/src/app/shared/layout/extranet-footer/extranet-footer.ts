import { Component } from '@angular/core';

@Component({
  selector: 'app-extranet-footer',
  standalone: true,
  templateUrl: './extranet-footer.html',
  styleUrl: './extranet-footer.scss',
})
export class ExtranetFooter {
  readonly yil = new Date().getFullYear();
}
