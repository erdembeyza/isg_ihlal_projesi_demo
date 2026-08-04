# Frontend (Angular)

İSG Kural İhlal Tespit ve Uyarı Sistemi'nin web arayüzü. Angular CLI 22 ile
standalone component mimarisiyle oluşturulmuştur (bkz. proje kökündeki
[`tasarim_mimari.md`](../tasarim_mimari.md) — BİLEŞENLER bölümü).

## Geliştirme sunucusunu çalıştırma

Backend'in `localhost:8080`'de ayakta olduğundan emin olun (bkz.
[`../backend/README.md`](../backend/README.md)), ardından:

```powershell
npm install
ng serve
```

`http://localhost:4200` adresinden erişilebilir; dosya değişikliklerinde
otomatik yeniden yüklenir. Geliştirme ortamında API adresi
`src/environments/environment.development.ts` içinde
`http://localhost:8080/api` olarak tanımlıdır.

## Klasör yapısı

```text
src/app/
  core/
    models/        Backend DTO'larına karşılık gelen TS interface'leri
    services/      AuthService, IhlalService, BolgeService, KullaniciService
    interceptors/  jwtInterceptor — her isteğe Authorization header'ı ekler
    guards/        authGuard, adminGuard, foremanGuard
    directives/    AuthImgDirective (JWT ile korumalı foto yükleme)
  features/
    login/                 COMPONENT-1
    admin-dashboard/       COMPONENT-2
    foreman-dashboard/     COMPONENT-3
  shared/
    components/            IhlalListesi, IstatistikGrafik, IhlalDetayModal
                           (COMPONENT-4/5/6)
```

## Test giriş bilgileri (yalnızca geliştirme ortamı)

| Kullanıcı adı | Şifre | Rol |
|---|---|---|
| `admin` | `Admin123!` | ISG_YONETICI |
| `formen1` | `Formen123!` | FORMEN |

`ai_core_servis` hesabı panel girişi için kullanılamaz (yalnızca AI Core API).

## Build

```powershell
ng build
```

Çıktı `dist/frontend` altında oluşur; `angular.json`'daki `development`
konfigürasyonu `environment.development.ts` dosyasını, `production`
konfigürasyonu ise varsayılan `environment.ts` dosyasını (bağıl `/api` yolu)
kullanır.
