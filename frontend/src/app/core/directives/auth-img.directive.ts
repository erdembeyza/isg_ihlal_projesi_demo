import { HttpClient } from '@angular/common/http';
import { Directive, ElementRef, OnDestroy, effect, inject, input } from '@angular/core';

/**
 * Ihlal kanit fotograflari "/uploads/**" altindan sunulur ve SecurityConfig
 * geregi gecerli bir JWT gerektirir (bkz. WebConfig). Duz bir <img src="...">
 * tarayicida Authorization header'i tasimadigindan 401 doner; bu direktif
 * fotografi HttpClient uzerinden (jwtInterceptor otomatik token ekler) blob
 * olarak cekip object URL'e cevirerek img'e atar.
 */
@Directive({
  selector: 'img[appAuthImg]',
  standalone: true,
})
export class AuthImgDirective implements OnDestroy {
  readonly appAuthImg = input.required<string | null | undefined>();

  private readonly http = inject(HttpClient);
  private readonly el = inject(ElementRef<HTMLImageElement>);
  private objectUrl: string | null = null;

  constructor() {
    effect(() => {
      const url = this.appAuthImg();
      this.eskiUrliTemizle();

      if (!url) {
        this.el.nativeElement.removeAttribute('src');
        return;
      }

      this.http.get(url, { responseType: 'blob' }).subscribe({
        next: (blob) => {
          this.objectUrl = URL.createObjectURL(blob);
          this.el.nativeElement.src = this.objectUrl;
        },
        error: () => this.el.nativeElement.removeAttribute('src'),
      });
    });
  }

  ngOnDestroy(): void {
    this.eskiUrliTemizle();
  }

  private eskiUrliTemizle(): void {
    if (this.objectUrl) {
      URL.revokeObjectURL(this.objectUrl);
      this.objectUrl = null;
    }
  }
}
