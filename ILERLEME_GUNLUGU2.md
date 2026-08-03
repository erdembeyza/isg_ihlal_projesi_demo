> **Not:** Ayrıntılı teknik günlük için bkz. [`ILERLEME_GUNLUGU.md`](./ILERLEME_GUNLUGU.md).

# İSG Kural İhlal Tespit ve Uyarı Sistemi — Proje Durum Raporu

**Son güncelleme:** 3 Ağustos 2026
**Rapor türü:** Yönetici özeti / hızlı durum panosu

---

## 1) Proje Nedir?

**Tek cümlelik amaç:** Fabrika/şantiye kameralarından gelen görüntüleri yapay
zeka ile analiz ederek kişisel koruyucu donanım (baret, yelek, gözlük) ihlallerini
otomatik tespit eden, kaydeden ve yetkili personele web arayüzü üzerinden
raporlayan bir İSG (İş Sağlığı ve Güvenliği) sistemi.

**3 katmanlı mimari:**

| Katman | Görevi | Durum |
|---|---|---|
| 🧠 **AI Core** (Python) | Kamera görüntüsünü YOLOv8/OpenCV ile analiz eder, ihlal tespit edince backend'e bildirir | Sırada (Faz 7) |
| ⚙️ **Backend** (Java/Spring Boot) | Kimlik doğrulama, ihlal kayıtlarının işlenmesi/saklanması, rol bazlı API (ISG_YONETICI / FORMEN) | ✅ Tamamlandı (Faz 2-4) — 8 endpoint de çalışıyor |
| 🖥️ **Frontend** (Angular) | Yöneticilerin ihlalleri görüntülediği, onayladığı/reddettiği web paneli | ✅ Tamamlandı (Faz 5-6) — giriş, yönetici/formen panelleri, grafik, detay modalı |

Detaylı veri modeli, DTO'lar, endpoint listesi ve bileşen hiyerarşisi için bkz.
[`tasarim_mimari.md`](./tasarim_mimari.md).

---

## 2) Genel İlerleme Durumu

Toplam **9 faz** (Faz 0 → Faz 8) planlanmış durumda. Her faz kendi git
branch'inde geliştirilip `--no-ff` ile `main`'e merge ediliyor ve GitHub'a
(`erdembeyza/isg_ihlal_projesi`) push ediliyor.

**İlerleme: 7 / 9 faz tamamlandı (%78)**

| Faz | Adı | Durum | Git Branch |
|---|---|---|---|
| Faz 0 | Ortam Kurulumu | ✅ Tamamlandı | `faz-0-ortam-kurulumu` |
| Faz 1 | Veritabanı | ✅ Tamamlandı | `faz-1-veritabani` |
| Faz 2 | Backend İskeleti | ✅ Tamamlandı | `faz-2-backend-iskeleti` |
| Faz 3 | Kimlik Doğrulama (JWT Security) | ✅ Tamamlandı | `faz-3-kimlik-dogrulama` |
| Faz 4 | İhlal Servisleri (API) | ✅ Tamamlandı | `faz-4-ihlal-servisleri` |
| Faz 5 | Frontend İskeleti (Angular) | ✅ Tamamlandı | `faz-5-frontend-iskeleti` |
| Faz 6 | Frontend Ekranları | ✅ Tamamlandı | `faz-6-frontend-ekranlari` |
| Faz 7 | AI Core (YOLOv8/OpenCV) | 🔄 Sırada | — *(henüz açılmadı)* |
| Faz 8 | Entegrasyon ve Kapanış | ⬜ Beklemede | — |

---

## 3) Teknoloji Yığını

### ✅ Kurulu ve Kullanımda

| Katman | Teknoloji |
|---|---|
| Backend dili/çatısı | Java 21 (JDK 21 — Eclipse Temurin 21.0.12+8), Spring Boot 4.1.0 |
| Backend bağımlılıkları | Spring Web, Spring Data JPA, Spring Security, Validation, Flyway |
| Kimlik doğrulama | JJWT 0.13.0 (JWT üretimi/doğrulaması), BCrypt |
| Veritabanı | PostgreSQL 16 (Alpine imajı, Docker) |
| DB migration | Flyway (10-alpine Docker imajı ile standalone çalıştırıldı; Faz 2 sonrası Spring Boot içinde otomatik) |
| Konteynerleştirme | Docker Desktop, docker-compose (postgres + pgAdmin servisleri) |
| DB yönetim arayüzü | pgAdmin 4 |
| Build aracı | Maven (Maven Wrapper — `mvnw`/`mvnw.cmd`) |
| Script/otomasyon | PowerShell (`scripts/flyway-migrate.ps1`) |
| Dosya depolama | Yerel dosya sistemi (`backend/uploads/`), `FileStorageService` üzerinden — ileride S3 gibi bir alternatife geçilebilir |
| Frontend çatısı | Angular 22 (standalone component mimarisi), Node.js 24.18.1, npm 11.16.0 |
| Frontend state/HTTP | Angular signals, `HttpClient` + fonksiyonel `HttpInterceptor` (JWT) |
| Grafik | Chart.js 4 + ng2-charts 10 (pasta grafik, istatistik ekranı) |

### ⬜ Planlanan (henüz kurulmadı)

| Katman | Teknoloji |
|---|---|
| AI / Bilgisayarlı Görü | Python 3.12, YOLOv8 (ultralytics), OpenCV — Faz 7 |
| AI Core yardımcı kütüphaneler | requests, numpy, python-dotenv — Faz 7 |

---

## 4) Kritik / Dikkat Çekici Notlar

- ⚠️ **Port 5432 çakışması (çözüldü):** Makinede Docker'dan bağımsız, native
  kurulu bir **PostgreSQL 18 Windows servisi** (`postgresql-x64-18`) 5432
  portunu işgal ediyordu; backend `isg_admin` kullanıcısıyla bağlanmaya
  çalıştığında yanlışlıkla bu native servise yönleniyor ve
  "password authentication failed" hatası veriyordu. Kullanıcı onayıyla bu
  servis durdurulup Disabled yapıldı; sonrasında backend Docker'daki
  Postgres'e (`isg_postgres`) sorunsuz bağlandı.
- 🖼️ **Foto erişimi JWT ile korunuyor:** İhlal kanıt fotoğrafları
  (`/uploads/**`) de tüm diğer `/api/**` uçları gibi geçerli bir JWT
  gerektirir; düz bir `<img src="...">` bu isteğe token ekleyemediği için
  401 alırdı. Frontend'de bunu çözmek için `AuthImgDirective` yazıldı —
  fotoğrafı `HttpClient` (interceptor otomatik token ekler) ile blob olarak
  çekip `URL.createObjectURL` ile `<img>`'e atıyor.
- 🔑 **Dev/test giriş bilgileri** (yalnızca geliştirme ortamı için, **üretimde
  kullanılmamalı**):

  | Kullanıcı adı | Şifre | Rol | Bölge |
  |---|---|---|---|
  | `admin` | `Admin123!` | ISG_YONETICI | Tüm fabrika |
  | `formen1` | `Formen123!` | FORMEN | Yuksek Firin-1 |

- 🗂️ Şema yönetimi tamamen Flyway'e devredildi (`spring.jpa.hibernate.ddl-auto=validate`);
  Hibernate şemayı değiştirmez, yalnızca migration'larla oluşturulan şemaya
  Entity'lerin uyup uymadığını doğrular.
- 🐞 **Faz 4'te bulunan ince Spring Security hatası (çözüldü):** Yetkisiz bir
  kullanıcı `@PreAuthorize` korumalı bir uca istek attığında beklenen 403
  yerine 401 dönüyordu. Kök neden: `sendError(403)` çağrısı Spring Boot'ta
  sunucu içinde `/error`'a forward yapıyor, bu forward güvenlik filtre
  zincirinden tekrar geçiyor ama JWT filtresi ikinci kez çalışmıyor (bu yüzden
  istek "kimliksiz" sayılıp 401'e dönüşüyordu). `SecurityConfig`'de `/error`
  yoluna `permitAll()` eklenerek düzeltildi.

---

## 5) Backend + Frontend Tamamlandı — Sıradaki Adım: Faz 7 (AI Core)

Backend (**8 endpoint**, rol bazlı erişim kontrolü dahil) ve Angular frontend
(giriş, yönetici paneli, formen paneli, istatistik grafiği, ihlal listesi,
detay modalı, reddetme aksiyonu, kullanıcı oluşturma formu) uçtan uca test
edilmiş ve çalışır durumda. Sırada Faz 7 (AI Core, Python/YOLOv8/OpenCV):

- Canlı kamera/RTSP akışının okunması, kişi + KDD (baret/yelek/gözlük)
  nesnelerinin YOLOv8 Nano ile tespiti.
- İhlal anında kare (snapshot) alınması ve yüz bölgesinin
  `cv2.GaussianBlur` ile bulanıklaştırılması (orijinal + blurlu kopya).
- Görsellerin base64'e çevrilip `POST /api/ihlaller`'a gönderilmesi.
- Kaggle test videolarıyla offline test/kalibrasyon modu.
