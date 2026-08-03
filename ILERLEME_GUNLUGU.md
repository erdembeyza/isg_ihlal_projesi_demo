# İSG İhlal Tespit Projesi — İlerleme Günlüğü

Bu doküman, projenin geliştirme sürecinde **şu ana kadar** yapılan işleri, kullanılan
araçları ve izlenen yöntemi faz faz özetler. Kaynak referans dokümanı
[`tasarim_mimari.md`](./tasarim_mimari.md)'dır. Genel yol haritası ve fazlar için
bkz. proje planı (Faz 0 → Faz 8).

**Son güncelleme:** 3 Ağustos 2026
**Şu ana kadar tamamlanan fazlar:** Faz 0 (Ortam Kurulumu), Faz 1 (Veritabanı),
Faz 2 (Backend İskeleti), Faz 3 (Kimlik Doğrulama), Faz 4 (İhlal Servisleri),
Faz 5 (Frontend İskeleti), Faz 6 (Frontend Ekranları), Faz 7 (AI Core),
Faz 8 (Entegrasyon ve Kapanış)
**Sıradaki faz:** — (tüm fazlar tamamlandı)

---

## Git Branch Stratejisi

Proje boyunca her faz için ayrı bir branch açılıyor, faz tamamlanınca `main`'e
`--no-ff` merge edilip hem `main` hem de faz branch'i `origin`'e (GitHub:
`erdembeyza/isg_ihlal_projesi`) push ediliyor. Böylece her fazın geçmişi ayrı
ayrı izlenebilir kalıyor, `main` her zaman derlenebilir/çalışır durumda tutuluyor.

```text
* 14bc975  Merge branch 'faz-1-veritabani'
|\
| * 1d29654  Faz 1: veritabani semasi (Flyway V1__init.sql) ve seed veri (V2__seed.sql)
|/
*   9d81b68  Merge branch 'faz-0-ortam-kurulumu'
|\
| * d1d3c27  Faz 0: ortam kurulumu - backend/frontend/ai-core klasorleri ve docker-compose.yml
|/
* 18a9778  tasarım dokümanı eklendi
```

| Branch | Durum | İçerik |
|---|---|---|
| `faz-0-ortam-kurulumu` | merge edildi | `.gitignore`, `ai-core/`, `docker-compose.yml`, `backend/`, `frontend/` iskelet klasörleri |
| `faz-1-veritabani` | merge edildi | Flyway migration'ları (`V1__init.sql`, `V2__seed.sql`), yardımcı script |
| `faz-2-backend-iskeleti` | merge edildi | Spring Boot 4.1.0 projesi, 5 Entity + 5 Repository |
| `faz-3-kimlik-dogrulama` | merge edildi | JJWT, `SecurityConfig`, `JwtService`, `JwtAuthenticationFilter`, `AuthController` |
| `faz-4-ihlal-servisleri` | merge edildi | `IhlalController`/`Service`, `KullaniciController`/`Service`, `BolgeController`, `FileStorageService`, `WebConfig` |
| `faz-5-frontend-iskeleti` | merge edildi | Angular 22 projesi, `AuthService`, `jwtInterceptor`, guard'lar, `LoginComponent`, dashboard iskeletleri, backend CORS ayarı |
| `faz-6-frontend-ekranlari` | merge edildi | `IhlalListesiComponent`, `IstatistikGrafikComponent`, `IhlalDetayModalComponent`, dolu dashboard içerikleri, `AuthImgDirective`, ikinci demo bölge (`V3__ikinci_bolge.sql`) |
| `faz-7-ai-core` | merge edildi | `ai-core/src/` (config, auth_client, backend_client, face_blur, ppe_detector, pipeline, main), test videosu üretme aracı, AI Core servis hesabı (`V4__ai_core_servis_hesabi.sql`) |
| `faz-8-entegrasyon-kapanis` | merge edildi | kök `README.md`, `scripts/e2e-smoke.ps1`, PPE model uyumu (`Person`/`person`), kapanış notları |

---

## Faz 0 — Ortam Kurulumu

### Ne yapıldı

- Proje kök dizininde `.gitignore` tanımlandı (Java/Maven `target/`, Angular
  `node_modules/`/`dist/`, Python `venv/`/`__pycache__/`, model ağırlıkları
  (`*.pt`) ve test videoları gibi büyük/geçici dosyalar hariç tutuldu).
- `docker-compose.yml` kök dizine eklendi (PostgreSQL + pgAdmin servisleri —
  detay için Faz 1 bölümüne bakınız).
- `ai-core/` klasörü ve `requirements.txt` (ultralytics, opencv-python,
  requests, numpy, python-dotenv) ile `.env.example` (Backend URL, video
  kaynağı, YOLO model yolu, güven eşiği, bölge ID gibi ayarlar) oluşturuldu.
- `backend/` ve `frontend/` klasörleri, Faz 2 ve Faz 5-6'da doldurulacak
  planları açıklayan birer `README.md` ile birlikte yer tutucu olarak
  oluşturuldu.
- Bu dosyalar diskte var olup commit edilmemişti; geriye dönük olarak
  `faz-0-ortam-kurulumu` branch'inde commit edilip `main`'e merge edildi.

### Kullanılan araçlar / komutlar

- **Git** — branch oluşturma, commit, merge, push (`git checkout -b`,
  `git add`, `git commit`, `git merge --no-ff`, `git push`)
- **PowerShell** — dosya/dizin keşfi (`Get-ChildItem`, `Get-Command`,
  `Get-Service`)

### Doğrulama sırasında tespit edilen ortam eksikleri

Ortamda şu araçlar kontrol edildi; bir kısmı PATH üzerinden erişilebilir
durumda değildi:

| Araç | Durum |
|---|---|
| Docker Desktop | Kurulu, servis durmuş halde bulundu → başlatıldı, sonrasında çalışır durumda |
| Python | 3.12.6 — çalışıyor |
| JDK 21 | `java -version` PATH'te bulunamadı / hata verdi |
| Node 22/24 (nvm-windows) | `node`, `nvm` PATH'te bulunamadı |
| Angular CLI | `ng` PATH'te bulunamadı |

> **Not:** JDK ve Node/Angular CLI kurulumu/PATH ayarı, Faz 2 (backend derleme)
> ve Faz 5-6 (Angular projesi) başlamadan önce tamamlanması gereken açık bir
> konudur.

---

## Faz 1 — Veritabanı

### Ne yapıldı

**1) PostgreSQL servisinin ayağa kaldırılması**

`docker-compose.yml` içinde tanımlı servisler:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: isg_postgres
    environment:
      POSTGRES_DB: isg_ihlal_db
      POSTGRES_USER: isg_admin
      POSTGRES_PASSWORD: isg_admin_pw
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U isg_admin -d isg_ihlal_db"]

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: isg_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@isg.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
```

Docker Desktop başlatıldı, `docker compose up` ile konteynerler ayağa
kaldırıldı ve `pg_isready` healthcheck'i ile hazır olduğu doğrulandı.

**2) Şema — Flyway migration olarak (`V1__init.sql`)**

Elle SQL çalıştırmak yerine `backend/src/main/resources/db/migration/V1__init.sql`
dosyasında **versiyonlanabilir** bir migration yazıldı (Faz 2'de Spring Boot +
Flyway projesi bu klasörü otomatik okuyacağı için ileride tekrar elle
uygulamaya gerek kalmayacak). İçeriği, `tasarim_mimari.md` > VERİ TABANI ve
DB CONSTRAINTS bölümlerine birebir uyumlu:

| Tablo | Amaç |
|---|---|
| `bolgeler` | Üretim bölgeleri (referans tablo) |
| `ihlal_tipleri` | KDD ihlal tipleri — BARET/YELEK/GOZLUK (referans tablo) |
| `kullanicilar` | Giriş yapan personel (ISG_YONETICI / FORMEN) |
| `ihlaller` | Ana işlem tablosu — AI Core'dan gelen ihlal kayıtları |
| `islem_loglari` | Denetim/audit log tablosu |

Uygulanan kısıtlar:

- `uq_kullanici_adi` — UNIQUE (`kullanicilar.kullanici_adi`)
- `ck_kullanici_rol` — CHECK (`rol IN ('ISG_YONETICI','FORMEN')`)
- `ck_ihlal_durum` — CHECK (`durum IN ('AKTIF','HATALI_TESPIT')`)
- `fk_kullanici_bolge`, `fk_ihlal_bolge` (ON DELETE RESTRICT), `fk_ihlal_tip`,
  `fk_ihlal_red_kullanici`, `fk_log_kullanici`, `fk_log_ihlal`
- Ek olarak, rol bazlı filtreleme (`WHERE bolge_id=...`) ve istatistik
  sorgularını hızlandırmak için `ihlaller` ve `islem_loglari` tablolarında
  performans indeksleri eklendi (dokümanda zorunlu tutulmasa da iyi pratik
  olarak dahil edildi).
- Tüm PK'ler `GENERATED BY DEFAULT AS IDENTITY` (Postgres kimlik sütunu)
  olarak tanımlandı; bu, hem otomatik artan ID üretimini hem de seed
  verisinde gerektiğinde ID belirtilebilmesini sağlıyor.

**3) Seed veri (`V2__seed.sql`)**

- İhlal tipleri: `BARET`, `YELEK`, `GOZLUK`
- Örnek bölge: `Yuksek Firin-1`
- 2 kullanıcı:

  | Kullanıcı adı | Şifre (yalnızca dev/test) | Rol | Bölge |
  |---|---|---|---|
  | `admin` | `Admin123!` | ISG_YONETICI | — (tüm fabrika) |
  | `formen1` | `Formen123!` | FORMEN | Yuksek Firin-1 |

- Şifreler **BCrypt** (cost=10) ile hash'lenip migration dosyasına yalnızca
  hash olarak yazıldı; düz metin şifreler repoya dahil edilmedi, hash'ler
  Python'da `bcrypt` kütüphanesiyle üretildi.

**4) Migration'ların uygulanması ve doğrulama**

Backend projesi (Faz 2) henüz kurulmadığı için migration'lar, standalone
**Flyway Docker imajı** (`flyway/flyway:10-alpine`) ile `isg_postgres`
konteynerinin bulunduğu `isg_ihlal_projesi_default` Docker ağı üzerinden
uygulandı:

```
Migrating schema "public" to version "1 - init"
Migrating schema "public" to version "2 - seed"
Successfully applied 2 migrations to schema "public", now at version v2
```

Bunu tekrarlanabilir kılmak için `scripts/flyway-migrate.ps1` PowerShell
script'i eklendi (`migrate` / `info` / `validate` / `clean` komutlarını
destekler).

Ardından doğrulama yapıldı:

- `\dt` ile 5 iş tablosu + `flyway_schema_history` tablosunun oluştuğu
  doğrulandı.
- Seed verisi (`SELECT * FROM bolgeler / ihlal_tipleri / kullanicilar`) ile
  içerik kontrol edildi.
- Kısıtların gerçekten çalıştığı canlı olarak test edildi:
  - Aynı `kullanici_adi` ile ikinci kayıt eklenmeye çalışıldı → `uq_kullanici_adi`
    hatası alındı ✅
  - Geçersiz bir `rol` değeriyle kayıt eklenmeye çalışıldı → `ck_kullanici_rol`
    hatası alındı ✅
  - Var olmayan bir `bolge_id` ile `ihlaller` tablosuna kayıt eklenmeye
    çalışıldı → `fk_ihlal_bolge` hatası alındı ✅
- Test sonrası tabloların temiz kaldığı (hatalı satırların işlenmediği)
  doğrulandı.

### Kullanılan araçlar / komutlar

- **Docker Desktop / Docker Engine** — `docker ps`, `docker network ls`,
  `docker inspect`, `docker exec`, `docker run`
- **PostgreSQL 16 (Alpine imajı)** — `psql` ile şema/veri doğrulama
- **Flyway 10 (Docker imajı, standalone)** — migration uygulama
- **Python 3.12 + `bcrypt` paketi** — şifre hash'i üretimi
- **PowerShell** — script ve komut orkestrasyonu

### Oluşturulan/değişen dosyalar

```
backend/
  README.md                                   (güncellendi — migration talimatları eklendi)
  src/main/resources/db/migration/
    V1__init.sql                              (yeni — şema + kısıtlar)
    V2__seed.sql                               (yeni — seed veri)
scripts/
  flyway-migrate.ps1                          (yeni — Flyway CLI yardımcı script)
```

---

## Faz 2 — Backend İskeleti

### Ne yapıldı

- JDK 21 (Eclipse Temurin) PATH'e eklendi ve doğrulandı.
- start.spring.io üzerinden Spring Boot 4.1.0 projesi oluşturuldu: Spring Web
  (webmvc), Spring Data JPA, Spring Security, PostgreSQL Driver, Validation,
  Flyway bağımlılıklarıyla.
- `application.yml` içinde DB bağlantı ayarları (`DB_URL`/`DB_USERNAME`/
  `DB_PASSWORD` env değişkenleriyle override edilebilir varsayılanlar),
  `spring.jpa.hibernate.ddl-auto=validate` (şema yönetimi tamamen Flyway'e
  bırakıldı), `spring.jpa.open-in-view=false`.
- `bolgeler`, `ihlal_tipleri`, `kullanicilar`, `ihlaller`, `islem_loglari`
  tablolarının her biri için JPA **Entity** sınıfı (`Bolge`, `IhlalTipi`,
  `Kullanici`, `Ihlal`, `IslemLog`) ve karşılık gelen **Repository**
  arayüzü (Spring Data JPA) yazıldı; `Rol` ve `IhlalDurumu` enum'ları
  veritabanındaki `CHECK` kısıtlarıyla birebir eşleşecek şekilde tanımlandı.
- Backend gerçekten derlendi, ayağa kalktı ve Flyway/Hibernate üzerinden
  Docker'daki PostgreSQL'e bağlanıp şemayı doğruladı.

### Tespit edilen ve çözülen sorun

- Makinede Docker'dan bağımsız native kurulu bir **PostgreSQL 18 Windows
  servisi** 5432 portunu işgal ediyordu; backend yanlışlıkla bu servise
  yönlenip "password authentication failed" hatası veriyordu. Native servis
  durdurulup devre dışı bırakılınca backend Docker'daki `isg_postgres`'e
  sorunsuz bağlandı.

---

## Faz 3 — Kimlik Doğrulama (JWT Security)

### Ne yapıldı

- `pom.xml`'e **JJWT** (`jjwt-api`/`jjwt-impl`/`jjwt-jackson`, 0.13.0)
  bağımlılıkları eklendi.
- `JwtService` — HMAC-SHA256 (Base64 secret, `jwt.secret` ayarından) ile
  token üretimi/doğrulaması. Token; `kullaniciId`, `rol`, `bolgeId` claim'lerini
  taşır, böylece sonraki her istekte veritabanına gitmeden rol/bölge bazlı
  yetkilendirme yapılabiliyor.
- `AuthenticatedUser` — JWT claim'lerinden çözülen, `@AuthenticationPrincipal`
  ile controller'larda enjekte edilebilen basit bir record.
- `JwtAuthenticationFilter` (`OncePerRequestFilter`) — `Authorization: Bearer
  ...` header'ını okur, geçerliyse `SecurityContext`'e authentication nesnesi
  yerleştirir (rol `ROLE_` önekiyle `GrantedAuthority` olarak eklenir);
  token yoksa/geçersizse isteği reddetmez, sadece kimliksiz bırakır — hangi
  endpoint'in kimlik gerektirdiğine `SecurityConfig` karar verir.
- `SecurityConfig` — CSRF kapalı (stateless JWT için gereksiz), session
  `STATELESS`, `/api/auth/**` herkese açık, diğer tüm `/api/**` kimlik
  doğrulama ister. Özel `authenticationEntryPoint` (401, "Kimlik dogrulama
  gerekli") ve `accessDeniedHandler` (403, "Bu islem icin yetkiniz yok").
  `@EnableMethodSecurity` ile `@PreAuthorize` kullanıma açıldı.
- `AuthController` — `POST /api/auth/login`: `KullaniciRepository.
  findByKullaniciAdi` ile kullanıcıyı bulur, `BCryptPasswordEncoder` ile
  şifreyi doğrular, `JwtService.generateToken` ile token üretir, rol/bölge
  bilgisiyle birlikte `LoginResponseDTO` döner. Hatalı şifre/kullanıcı adı
  `BadCredentialsException` → 401.
- Postman ile `admin`/`Admin123!` ve `formen1`/`Formen123!` ile giriş
  denendi, gerçek JWT alındığı ve doğru claim'leri (rol, bölge) taşıdığı
  doğrulandı.

---

## Faz 4 — İhlal Servisleri (API)

### Ne yapıldı

Tasarım dokümanındaki (`tasarim_mimari.md`) 7 endpoint (login hariç, o Faz
3'te tamamlanmıştı) uçtan uca yazıldı ve test edildi:

| Endpoint | Method | Rol kısıtı | Açıklama |
|---|---|---|---|
| `/api/ihlaller` | POST | kimliği doğrulanmış (AI Core için) | Yeni ihlal kaydı — foto Base64 olarak gelir, diske yazılır |
| `/api/ihlaller` | GET | ISG_YONETICI / FORMEN | Rol bazlı filtre: Formen kendi `bolge_id`'si + blurlu foto, Yönetici tüm fabrika + orijinal foto |
| `/api/ihlaller/{id}` | GET | ISG_YONETICI / FORMEN | Formen başka bölgenin kaydına erişmeye çalışırsa 403 |
| `/api/ihlaller/{id}/reddet` | POST | **ISG_YONETICI** | Durumu `HATALI_TESPIT` yapar, `islem_loglari`'na kayıt düşer |
| `/api/ihlaller/istatistik` | GET | ISG_YONETICI / FORMEN | Bölge+tip bazlı haftalık toplam ve önceki haftaya göre yüzde değişim |
| `/api/bolgeler` | GET | kimliği doğrulanmış | Tüm bölgeleri listeler (dropdown/filtre için) |
| `/api/kullanicilar` | POST | **ISG_YONETICI** | Yeni formen/kullanıcı tanımlar |

Bileşenler:

- **DTO'lar** — `IhlalKayitRequestDTO`, `IhlalResponseDTO`, `IhlalRedRequestDTO`,
  `IhlalIstatistikDTO`, `BolgeDTO`, `KullaniciRequestDTO`, `KullaniciResponseDTO`
  (hepsi `jakarta.validation` anotasyonlarıyla).
- **`FileStorageService`** — Base64 foto içeriğini (data URI öneki de kabul
  edilir) diske (`backend/uploads/ihlaller/`) `UUID` isimle yazar, DB'ye
  yalnızca bağıl URL yolu (`/uploads/ihlaller/...`) işlenir.
- **`WebConfig`** — `/uploads/**` altını statik dosya olarak sunar (kendisi de
  JWT ile korunur, çünkü `SecurityConfig`'deki `anyRequest().authenticated()`
  kuralına tabidir).
- **`IhlalService`** — kaydet/listele/detay/reddet/istatistik iş mantığı.
  Formen kısıtı (`WHERE bolge_id = ...`) ve foto seçimi (yönetici: orijinal,
  formen: blurlu) burada uygulanıyor. İstatistik hesaplaması Java tarafında
  `Collectors.groupingBy` ile (bölge, ihlal tipi) anahtarına göre gruplanıp,
  bu hafta / önceki hafta karşılaştırması yapılıyor.
- **`KullaniciController`/`Service`**, **`BolgeController`** — kalan iki uç.

### Karşılaşılan ve çözülen 2 hata

1. **`LazyInitializationException` (500, "401" gibi görünen)** — `application.
   yml`'de `open-in-view: false` olduğu için, `IhlalService.toDto()` içinde
   `ihlal.getBolge().getBolgeAdi()` gibi **LAZY** ilişkilere Hibernate
   session'ı kapandıktan sonra erişilmeye çalışılıyordu. Çözüm: `IhlalService`
   sınıfına `@Transactional(readOnly = true)` (varsayılan), yazma yapan
   `kaydet`/`reddet` metotlarına ise kendi `@Transactional`'ları eklendi —
   böylece DTO dönüşümü sırasında session açık kalıyor.
2. **403 yerine 401 dönmesi (formen'in yetkisiz endpoint denemelerinde)** —
   `accessDeniedHandler`'ın çağırdığı `response.sendError(403, ...)`, Spring
   Boot'ta sunucu içinde `/error`'a **forward** yapıyor. Bu forward güvenlik
   filtre zincirinden tekrar geçiyor; ama `JwtAuthenticationFilter`
   (`OncePerRequestFilter` olduğu için) bu ikinci geçişte tekrar çalışmıyor,
   yani istek "kimliksiz" sayılıyor. Bu da ikinci bir güvenlik reddine (401,
   `authenticationEntryPoint` üzerinden) yol açıp orijinal 403'ün üzerine
   yazılmasına neden oluyordu. Kök neden, Spring Security debug logları
   (`org.springframework.security: debug`) geçici olarak açılıp istek akışı
   satır satır incelenerek bulundu. **Çözüm:** `SecurityConfig`'de `/error`
   yoluna `permitAll()` eklendi — böylece forward edilen istek ikinci bir
   güvenlik reddine uğramıyor ve orijinal (doğru) durum kodu korunuyor.

### Doğrulama

PowerShell ile uçtan uca senaryo test edildi: admin+formen login → bölge
listesi → yeni ihlal kaydı (POST, foto diske yazılıyor) → listeleme (admin
tüm liste + orijinal foto, formen sadece kendi bölgesi + blurlu foto) →
detay → istatistik → formen'in reddetme denemesi (403 ✅) → admin'in
reddetmesi (durum `HATALI_TESPIT`'e döndü ✅) → formen'in kullanıcı oluşturma
denemesi (403 ✅) → admin'in yeni formen oluşturması (201 ✅).

### Kullanılan araçlar / komutlar

- **Maven Wrapper** (`mvnw.cmd compile`, `mvnw.cmd spring-boot:run`)
- **PowerShell** (`Invoke-RestMethod`/`Invoke-WebRequest`) — API testleri
- Spring Security **DEBUG logging** — 401/403 hatasının kök nedenini bulmak
  için geçici olarak açılıp, çözüldükten sonra kapatıldı

---

## Faz 5 — Frontend İskeleti (Angular)

### Ne yapıldı

- Ortamda Node.js 24.18.1, npm 11.16.0 ve Angular CLI 22.1.2'nin zaten kurulu
  olduğu tespit edildi (Faz 0'da "eksik" olarak not edilmişti, bu engel
  ortadan kalkmıştı).
- Yer tutucu `frontend/README.md` kenara alınıp `ng new frontend --routing
  --style=scss --skip-git` ile gerçek Angular 22 projesi (standalone
  component mimarisi) oluşturuldu.
- **Environment ayarları:** `environment.ts` (üretim, bağıl `/api` yolu) ve
  `environment.development.ts` (`http://localhost:8080/api`), `angular.json`
  içinde `development` konfigürasyonu için `fileReplacements` eklendi.
- **Backend DTO'larına karşılık gelen TS modelleri:** `auth.model.ts`,
  `bolge.model.ts`, `ihlal.model.ts`, `kullanici.model.ts` (`core/models/`).
- **`AuthService`** — signal tabanlı oturum yönetimi; `LoginResponseDTO`'yu
  `localStorage`'da saklar, `isLoggedIn`/`rol`/`isYonetici`/`isFormen`
  computed signal'leri sunar.
- **`jwtInterceptor`** — fonksiyonel HTTP interceptor; her isteğe
  `Authorization: Bearer <token>` ekler (`/auth/login` hariç), 401 yanıtında
  otomatik oturumu kapatıp giriş ekranına yönlendirir.
- **Guard'lar** — `authGuard` (genel oturum kontrolü), `adminGuard` (yalnızca
  ISG_YONETICI), `foremanGuard` (yalnızca FORMEN).
- **`LoginComponent`** — Reactive Forms ile kullanıcı adı/şifre doğrulaması,
  `/api/auth/login` çağrısı, role göre yönlendirme, hatalı girişte uyarı.
- **`AdminDashboard`/`ForemanDashboard`** — Faz 6'da doldurulacak iskelet
  bileşenler (yalnızca hoş geldin başlığı + çıkış butonu).
- **Routing** (`app.routes.ts`) — `/giris`, `/yonetici` (adminGuard), `/formen`
  (foremanGuard), `''` ve `**` → `/giris`.
- **Backend'de CORS ayarı** (`SecurityConfig.java`) — Angular'ın
  `localhost:4200`'den `localhost:8080`'e istek atabilmesi için
  `CorsConfigurationSource` bean'i eklendi.

### Doğrulama

Bir tarayıcı otomasyon ajanıyla 10 senaryo uçtan uca test edildi (kök
yönlendirme, giriş yapmadan `/yonetici`'ye erişim engeli, boş form
doğrulaması, admin girişi + doğru panele yönlendirme, formen'in
`/yonetici`'ye erişememesi, çıkış yapma, formen girişi + doğru panele
yönlendirme, admin'in `/formen`'e erişememesi, tekrar çıkış, yanlış şifreyle
giriş denemesi). Hepsi başarılı, CORS hatası dahil hiçbir hata gözlenmedi.

---

## Faz 6 — Frontend Ekranları

### Ne yapıldı

Tasarım dokümanındaki (`tasarim_mimari.md`) COMPONENT-2 → COMPONENT-6 arası
tüm bileşenler dolduruldu ve dashboard'lar gerçek veriyle çalışır hale
getirildi:

- **`IhlalService`/`BolgeService`/`KullaniciService`** (`core/services/`) —
  `/api/ihlaller`, `/api/bolgeler`, `/api/kullanicilar` uçlarına karşılık
  gelen `HttpClient` çağrıları. `IhlalService.fotoTamUrl()`, backend'in
  döndürdüğü bağıl `/uploads/...` yolunu `environment.apiUrl`'den türetilen
  origin ile tam URL'e çevirir.
- **`AuthImgDirective`** (`core/directives/`) — ihlal kanıt fotoğrafları
  `/uploads/**` altından JWT ile korunur (bkz. `WebConfig`/`SecurityConfig`),
  düz bir `<img src="...">` bu isteği kimliksiz atacağından 401 alır. Bu
  direktif fotoğrafı `HttpClient` üzerinden (interceptor otomatik token
  ekler) blob olarak çekip `URL.createObjectURL` ile `img`'e atar,
  `ngOnDestroy`'da object URL'i serbest bırakır.
- **`IhlalListesiComponent`** (`shared/components/`) — ihlal tablosu;
  bölge/tip/tarihe göre sıralama (tıklanabilir başlıklar), sayfalama (8
  satır/sayfa), satır tıklamasını `satirSecildi` output'uyla dışarı bildirir.
  Filtreleme sorumluluğu üst dashboard bileşenlerinde.
- **`IstatistikGrafikComponent`** — `ng2-charts`/`chart.js` ile ihlal
  tiplerinin pasta grafiği + son 7 gün toplam adedi + en belirgin 5
  bölge/tip kırılımının yüzdesel değişim listesi (artış kırmızı, azalış
  yeşil). Grafik dilimine tıklamak `tipSecildi` output'u ile üst bileşene
  filtre isteği gönderir.
- **`IhlalDetayModalComponent`** — seçilen ihlalin büyük fotoğrafı
  (`AuthImgDirective`), bölge/tip/zaman/durum bilgisi; `yetkiliMi=true` ve
  durum `AKTIF` ise "Hatalı Tespit Olarak İşaretle" butonu + opsiyonel
  gerekçe formu. Gerçek API çağrısını yapmaz, `reddet` output'uyla üst
  bileşene bildirir (state/servis sorumluluğu dashboard'larda).
- **`AdminDashboard`** — tüm fabrika verisini çeker, bölge + ihlal tipi
  dropdown filtreleri, istatistik grafiği, ihlal listesi, detay modalı,
  reddetme aksiyonu (başarılı reddetmede liste+istatistik yeniden yüklenir).
  Ayrıca `KullaniciRequestDTO`/`ResponseDTO` modellerini kullanan bir "Yeni
  Kullanıcı" formu eklendi (yalnızca ISG_YONETICI'ye görünür, FORMEN rolü
  seçilirse bölge seçimi zorunlu kılınır, 409 kullanıcı adı çakışması
  kullanıcıya mesaj olarak gösterilir).
- **`ForemanDashboard`** — backend zaten JWT'deki `bolgeId`'ye göre kapsamı
  kısıtladığından ekstra bölge filtresi yok; yalnızca tip filtresi, istatistik
  grafiği ve en belirgin yüzde değişime göre üstte bir "trend" bilgi kutusu
  (ör. "Bu hafta GÖZLÜK ihlalleri geçen haftaya göre %100 arttı") gösterir.
  Reddet butonu hiçbir yerde render edilmez.
- **`app.config.ts`** — `provideCharts(withDefaultRegisterables())` eklendi.
- **Backend:** `V3__ikinci_bolge.sql` migration'ı eklendi (V1/V2'yi
  değiştirmeden, ikinci bir test bölgesi — "Sicak Haddehane-2" — ekler),
  böylece admin panelindeki bölge filtresi anlamlı test edilebiliyor.

### Doğrulama

Backend ve Angular dev sunucuları ayağa kaldırıldı, admin token'ı ile API
üzerinden 13 adet demo ihlal kaydı (1x1 piksel test görseli, karışık
bölge/tip/tarih) oluşturuldu (kullanıcı onayı alınarak). Ardından bir
tarayıcı otomasyon ajanıyla uçtan uca test edildi:

- Admin girişi → pasta grafiği + ihlal listesi + thumbnail fotoğrafların
  (JWT korumalı `/uploads` ucu üzerinden, `AuthImgDirective` ile) sorunsuz
  yüklendiği doğrulandı.
- Bölge filtresi ("Sicak Haddehane-2") ve tip filtresi (ör. "BARET") listeyi
  ve istatistik grafiğini doğru şekilde daralttı.
- Bir kayda tıklanıp detay modalı açıldı, büyük fotoğraf yüklendi, "Hatalı
  Tespit Olarak İşaretle" → gerekçe girildi → "Reddi Onayla" ile kayıt
  `HATALI_TESPIT`'e döndü, liste ve istatistik otomatik yenilendi.
- "+ Yeni Kullanıcı" formu açılıp alanları doğrulandı (submit edilmedi).
- Çıkış yapılıp formen ile giriş yapıldı: yalnızca "Yuksek Firin-1"
  bölgesine ait kayıtlar listelendi, reddet butonu hiçbir yerde
  görünmüyor, trend bilgi kutusu doğru hesaplanmış yüzdeyle gösterildi.
- Tarayıcı konsolunda CORS/401/403/500 veya JS hatası gözlenmedi.

### Kullanılan araçlar / komutlar

- **`ng build`/`ng serve`** — derleme ve geliştirme sunucusu doğrulaması
- **Maven Wrapper** (`mvnw.cmd spring-boot:run`) — backend'in V3 migration'ı
  uygulayarak yeniden başlatılması
- **PowerShell** (`Invoke-RestMethod`) — demo ihlal verisi üretimi
- **Tarayıcı otomasyon ajanı** — 8 senaryoluk uçtan uca test

---

## Faz 7 — AI Core (YOLOv8/OpenCV)

### Ne yapıldı

- **Backend: AI Core servis hesabı** — `POST /api/ihlaller` özel bir rol
  kısıtı taşımasa da (bkz. Faz 4), herhangi bir kimlik doğrulanmış istemci
  gerektirdiği için `V4__ai_core_servis_hesabi.sql` migration'ı ile
  `ai_core_servis` (rol: `ISG_YONETICI`, `bolge_id`: NULL) adında dev/test
  amaçlı bir servis hesabı eklendi. AI Core, backend'e karşı normal bir
  kullanıcı gibi `/api/auth/login` ile giriş yapıp JWT alıyor.
- **`ai-core/src/config.py`** — `.env` dosyasını okuyup tip dönüşümü/yol
  çözümlemesi yapan merkezi ayar modülü (backend adresi, servis hesabı
  bilgileri, video kaynağı, YOLO model yolu, güven eşiği, bölge ID,
  ihlal tipi ID eşlemesi, cooldown süresi, frame atlama).
- **`ai-core/src/auth_client.py`** — `BackendOturumu`: login olup JWT'yi
  önbellekte tutan, süresi dolmadan (50 dk eşik, backend süresi 60 dk)
  kendiliğinden yenileyen istemci.
- **`ai-core/src/backend_client.py`** — kareyi JPEG+base64'e çevirip
  `IhlalKayitRequestDTO` formatında `POST /api/ihlaller`'a gönderen istemci;
  401 alırsa token'ı zorla yenileyip bir kez daha dener.
- **`ai-core/src/face_blur.py`** — KVKK gereği yüz bulanıklaştırma: OpenCV'nin
  paketle birlikte gelen Haar Cascade yüz dedektörüyle kişi kutusu içinde
  yüz aranır, bulunursa `cv2.GaussianBlur` ile sansürlenir; yüz hiç
  bulunamazsa güvenlik ağı olarak kişi kutusunun üst çeyreği blurlanır
  (KVKK riskini sıfırlamak için).
- **`ai-core/src/ppe_detector.py`** — YOLOv8 modelini yükleyip sınıf
  isimlerini (ör. `NO-Hardhat`, `NO-Safety Vest`, `NO-Goggles` — yaygın
  açık kaynak "Construction Site Safety" veri kümesi kalıpları) ihlal
  tipine (`BARET`/`YELEK`/`GOZLUK`) çeviren dedektör. `models/ppe_yolov8n.pt`
  bulunamazsa (henüz gerçek bir PPE modeli eğitilip yerleştirilmediyse)
  ultralytics'in COCO ön-eğitilmiş `yolov8n.pt` modeline düşüp yalnızca
  `person` sınıfıyla çalışan **DEMO_MODU**'na geçer; bu modda tespit edilen
  her kişi, boru hattının (yakalama→blur→backend POST) uçtan uca
  doğrulanabilmesi için tüm ihlal tipleriyle işaretlenir ve bu açıkça
  `WARNING` olarak loglanır (gerçek üretim tespiti değildir).
- **`ai-core/src/pipeline.py` / `main.py`** — video kaynağını (RTSP ya da
  dosya) okuyan, `FRAME_ATLAMA` kadar karede bir YOLO çalıştıran, ihlal tipi
  başına `DETECTION_COOLDOWN_SANIYE` (varsayılan 30 sn) ile tekrar
  bildirimini (spam) engelleyen ana döngü. CLI bayrakları: `--source`,
  `--dry-run` (backend'e göndermez, `--debug-output` ile kareleri diske
  yazar), `--show` (tespit kutularını pencerede gösterir), `--loop` (video
  dosyasını başa sararak canlı akışı simüle eder), `--verbose`.
- **`ai-core/tools/test_video_uret.py`** — Kaggle hesabı/interneti
  gerektirmeden, `ultralytics` paketiyle gelen (içinde gerçek insan olan)
  örnek görselden küçük bir test videosu üreten yardımcı script; gerçek
  kullanımda Kaggle'daki açık kaynak İSG videolarıyla değiştirilmesi
  gerektiği `README.md`'de not edildi.
- **`ai-core/README.md`** — kurulum, çalıştırma, DEMO_MODU'nun ne anlama
  geldiği ve gerçek bir PPE modeline nasıl geçileceği anlatıldı.
- `.gitignore`'a `ai-core/debug_output/` ve kök dizine inebilecek
  `ai-core/*.pt` (ör. `yolov8n.pt` otomatik indirmesi) eklendi.

### Neden bu şekilde tasarlandı (DEMO_MODU)

Gerçek bir baret/yelek/gözlük-eksikliği YOLO modelini bu ortamda sıfırdan
eğitmek (etiketli veri seti + GPU + saatler süren eğitim) faz kapsamının
dışında; bunun yerine kod, gerçek bir PPE modeli `models/ppe_yolov8n.pt`'e
yerleştirildiğinde (sınıf isimleri `NO-Hardhat` vb. olduğu sürece) hiçbir
kod değişikliği gerekmeden doğrudan çalışacak şekilde tasarlandı. Modelin
henüz mevcut olmadığı durumda ise boru hattının geri kalanının (kişi
tespiti → yüz blur → base64 → JWT ile backend'e POST → veritabanına yazma)
**gerçekten** çalıştığı, sahte/mock veri değil gerçek YOLOv8 çıkarımıyla
uçtan uca doğrulandı (bkz. Test bölümü).

### Test / Doğrulama

1. `ai-core/venv` içinde `pip install -r requirements.txt` ile `ultralytics`
   8.3.40, `torch` 2.13, `opencv-python` 4.10 vb. bağımlılıkların kurulu
   olduğu doğrulandı.
2. `tools/test_video_uret.py` ile 30 karelik bir demo videosu üretildi
   (ultralytics'in örnek `bus.jpg` görseli — içinde gerçek insanlar var).
3. **Kuru çalıştırma (`--dry-run --debug-output`):** DEMO_MODU'na düşüldüğü,
   kişinin tespit edildiği, cooldown'ın aynı ihlal tipini tekrar
   bildirmediği (30 karede yalnızca 1'er BARET/YELEK/GOZLUK) ve üretilen
   blurlu karede yüzün gerçekten bulanıklaştırıldığı (orijinal/blur kare
   çiftleri görsel olarak karşılaştırılarak) doğrulandı.
4. **Uçtan uca (gerçek backend):** `mvnw spring-boot:run` ile backend
   başlatılıp Flyway'in `V4` migration'ını uyguladığı (`Current version of
   schema "public": 4`) doğrulandı; `ai_core_servis` hesabıyla
   `/api/auth/login` başarılı oldu; `python -m src.main` (dry-run OLMADAN)
   çalıştırılıp 3 ihlal (`id=18` BARET, `id=19` YELEK, `id=20` GOZLUK)
   gerçekten `POST /api/ihlaller` ile backend'e gönderildi ve
   veritabanına yazıldı; `admin` hesabıyla `GET /api/ihlaller` çağrılarak
   bu 3 kaydın `Yuksek Firin-1` bölgesinde, `AKTIF` durumda listelendiği
   teyit edildi.

### Kullanılan araçlar / komutlar

- **Python 3.12 + venv** — bağımlılık kurulumu (`pip install -r requirements.txt`)
- **`python -m src.main`** — AI Core CLI (`--dry-run`, `--debug-output`, `--verbose`)
- **Maven Wrapper** (`mvnw.cmd spring-boot:run`) — backend'in `V4` migration'ı
  uygulayarak başlatılması
- **PowerShell** (`Invoke-RestMethod`) — servis hesabı girişi ve
  `GET /api/ihlaller` ile doğrulama
- **Docker** (`docker ps`) — PostgreSQL/pgAdmin konteynerlerinin ayakta
  olduğunun kontrolü

---

## Faz 8 — Entegrasyon ve Kapanış

### Ne yapıldı

- **`tasarim_mimari.md` MODÜL-1…6** kapsamındaki üç katman, gerçek PPE
  modeli (`ai-core/models/ppe_yolov8n.pt`, Colab’da Construction Site Safety
  ile fine-tune) ile tekrar uçtan uca doğrulandı:
  AI Core (demo_modu=False) → JWT login (`ai_core_servis`) →
  `POST /api/ihlaller` (YELEK/BARET) → admin `GET` + formen kapsamı
  (blurlu foto, orijinal sızdırmaz) → istatistik → `POST .../reddet`
  (MODÜL-6, `HATALI_TESPIT`).
- **`scripts/e2e-smoke.ps1`** — bu doğrulamayı tekrarlanabilir kılan duman
  testi (backend ayaktayken repo kökünden çalıştırılır).
- **Kök `README.md`** — docker → backend → frontend → AI Core hızlı
  başlatma, rol tablosu, bilinen sınırlamalar (kapanış).
- **`ppe_detector.py`** — Roboflow PPE modellerindeki `Person` sınıfı ile
  COCO `person` sınıfının ikisi de kabul edilir (yüz blur eşlemesi).
- **`ai-core/README.md`** — eğitilmiş modelin yerleştirildiği varsayımı ve
  GOZLUK (`NO-Goggles` sette yok) sınırı güncellendi.

### Tasarım checklist (kapanış)

| Modül | Durum |
|---|---|
| MODÜL-1 AI Core (tespit, blur, POST, offline video) | ✅ |
| MODÜL-2 Backend API (kayıt, liste, istatistik, reddet) | ✅ |
| MODÜL-3 JWT Security (login, guard, interceptor, PreAuthorize) | ✅ |
| MODÜL-4 Admin Dashboard | ✅ (Faz 5–6) |
| MODÜL-5 Formen Dashboard | ✅ (Faz 5–6) |
| MODÜL-6 Audit & Feedback (HATALI_TESPIT + islem_loglari) | ✅; “reddedilen görseller havuzu” tasarımda ileriki fine-tune için bırakıldı |

### Bilinen sınırlamalar (kapanış notu)

- Eğitilen modelde **GOZLUK / `NO-Goggles` yok**; BARET ve YELEK tespit edilir.
- Canlı RTSP yerine geliştirmede yerel/Kaggle videosu kullanılır
  (`VIDEO_SOURCE`); Kaggle dosyası `ai-core/test_videos/` altına konur.
- `.pt` ağırlıkları git’e alınmaz; her ortamda `models/ppe_yolov8n.pt`
  ayrıca yerleştirilmelidir.

### Test / Doğrulama

`powershell -File scripts/e2e-smoke.ps1` — admin/AI Core login, 2 yeni ihlal
(id 23–24), formen KVKK kontrolü, istatistik, reddet (id=24 → HATALI_TESPIT).

### Kullanılan araçlar

- PowerShell (`scripts/e2e-smoke.ps1`, `Invoke-RestMethod`)
- AI Core CLI (`python -m src.main`)
- Docker PostgreSQL (zaten ayakta), çalışan Spring Boot (port 8080)
