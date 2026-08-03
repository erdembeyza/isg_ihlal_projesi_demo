# İSG İhlal Tespit Projesi — İlerleme Günlüğü

Bu doküman, projenin geliştirme sürecinde **şu ana kadar** yapılan işleri, kullanılan
araçları ve izlenen yöntemi faz faz özetler. Kaynak referans dokümanı
[`tasarim_mimari.md`](./tasarim_mimari.md)'dır. Genel yol haritası ve fazlar için
bkz. proje planı (Faz 0 → Faz 8).

**Son güncelleme:** 3 Ağustos 2026
**Şu ana kadar tamamlanan fazlar:** Faz 0 (Ortam Kurulumu), Faz 1 (Veritabanı),
Faz 2 (Backend İskeleti), Faz 3 (Kimlik Doğrulama), Faz 4 (İhlal Servisleri)
**Sıradaki faz:** Faz 5-6 (Frontend — Angular)

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
| `faz-4-ihlal-servisleri` | geliştiriliyor (bu günlük güncellemesiyle commit edilecek) | `IhlalController`/`Service`, `KullaniciController`/`Service`, `BolgeController`, `FileStorageService`, `WebConfig` |

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

## Sırada Ne Var — Faz 5-6 (Frontend, Angular)

- Node.js (22/24) ve Angular CLI kurulumu — ortamda hâlâ PATH'te değil,
  bu faza başlamadan önce halledilmesi gerekiyor.
- `ng new` ile Angular projesinin oluşturulması.
- Giriş ekranı, yönetici paneli (tüm fabrika + istatistik grafiği + reddetme
  aksiyonu), formen paneli (kendi bölgesi + blurlu foto) bileşenleri.
- Backend'deki 8 endpoint'e karşılık gelen Angular servisleri (`HttpClient`
  + JWT'nin `Authorization` header'ına eklenmesi için bir `HttpInterceptor`).
