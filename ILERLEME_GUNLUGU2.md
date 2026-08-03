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
| 🧠 **AI Core** (Python) | Kamera görüntüsünü YOLOv8/OpenCV ile analiz eder, ihlal tespit edince backend'e bildirir | ✅ Tamamlandı (Faz 7) — uçtan uca test edildi (bkz. not) |
| ⚙️ **Backend** (Java/Spring Boot) | Kimlik doğrulama, ihlal kayıtlarının işlenmesi/saklanması, rol bazlı API (ISG_YONETICI / FORMEN) | ✅ Tamamlandı (Faz 2-4) — 8 endpoint de çalışıyor |
| 🖥️ **Frontend** (Angular) | Yöneticilerin ihlalleri görüntülediği, onayladığı/reddettiği web paneli | ✅ Tamamlandı (Faz 5-6) — giriş, yönetici/formen panelleri, grafik, detay modalı |

Detaylı veri modeli, DTO'lar, endpoint listesi ve bileşen hiyerarşisi için bkz.
[`tasarim_mimari.md`](./tasarim_mimari.md).

---

## 2) Genel İlerleme Durumu

Toplam **9 faz** (Faz 0 → Faz 8) planlanmış durumda. Her faz kendi git
branch'inde geliştirilip `--no-ff` ile `main`'e merge ediliyor ve GitHub'a
(`erdembeyza/isg_ihlal_projesi`) push ediliyor.

**İlerleme: 8 / 9 faz tamamlandı (%89)**

| Faz | Adı | Durum | Git Branch |
|---|---|---|---|
| Faz 0 | Ortam Kurulumu | ✅ Tamamlandı | `faz-0-ortam-kurulumu` |
| Faz 1 | Veritabanı | ✅ Tamamlandı | `faz-1-veritabani` |
| Faz 2 | Backend İskeleti | ✅ Tamamlandı | `faz-2-backend-iskeleti` |
| Faz 3 | Kimlik Doğrulama (JWT Security) | ✅ Tamamlandı | `faz-3-kimlik-dogrulama` |
| Faz 4 | İhlal Servisleri (API) | ✅ Tamamlandı | `faz-4-ihlal-servisleri` |
| Faz 5 | Frontend İskeleti (Angular) | ✅ Tamamlandı | `faz-5-frontend-iskeleti` |
| Faz 6 | Frontend Ekranları | ✅ Tamamlandı | `faz-6-frontend-ekranlari` |
| Faz 7 | AI Core (YOLOv8/OpenCV) | ✅ Tamamlandı | `faz-7-ai-core` |
| Faz 8 | Entegrasyon ve Kapanış | 🔄 Sırada | — *(henüz açılmadı)* |

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
| AI / Bilgisayarlı Görü | Python 3.12, YOLOv8 Nano (ultralytics 8.3.40), OpenCV 4.10, PyTorch 2.13 |
| AI Core yardımcı kütüphaneler | requests, numpy, python-dotenv |

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
  | `ai_core_servis` | `AiCore123!` | ISG_YONETICI | Tüm fabrika (yalnızca `POST /api/ihlaller` için kullanılır) |

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

## 5) Üç Katman da Tamamlandı — Sıradaki Adım: Faz 8 (Entegrasyon ve Kapanış)

Backend (**8 endpoint**, rol bazlı erişim kontrolü dahil), Angular frontend
(giriş, yönetici paneli, formen paneli, istatistik grafiği, ihlal listesi,
detay modalı, reddetme aksiyonu, kullanıcı oluşturma formu) ve AI Core
(YOLOv8 tabanlı tespit → yüz blur → backend'e POST) uçtan uca test edilmiş
ve çalışır durumda.

**Faz 7 (AI Core) özeti:**

- `ai-core/src/` altında YOLOv8 Nano tabanlı tespit motoru
  (`ppe_detector.py`), yüz blur (`face_blur.py`, Haar Cascade +
  `cv2.GaussianBlur`), backend istemcisi (`auth_client.py` +
  `backend_client.py`, JWT ile giriş/yenileme) ve ana döngü
  (`pipeline.py`/`main.py`, cooldown + frame atlama + `--dry-run`/`--show`/
  `--loop` bayrakları) yazıldı.
- Backend'e AI Core için özel bir servis hesabı eklendi
  (`V4__ai_core_servis_hesabi.sql`, `ai_core_servis` / dev-only şifre).
- ⚠️ **DEMO_MODU notu:** Gerçek bir baret/yelek/gözlük-eksikliği modeli
  henüz eğitilip `ai-core/models/ppe_yolov8n.pt`'e yerleştirilmedi (bu,
  etiketli veri seti + eğitim süresi gerektiren ayrı bir iş). Bu dosya
  yoksa sistem otomatik olarak COCO ön-eğitilmiş `yolov8n.pt`'e düşüp
  yalnızca "person" sınıfıyla çalışan bir DEMO_MODU'na geçiyor (tespit
  edilen her kişi, boru hattını test etmek için tüm ihlal tipleriyle
  işaretleniyor — gerçek tespit değil). Kod, gerçek bir PPE modeli
  yerleştirildiğinde herhangi bir değişiklik gerekmeden çalışacak şekilde
  tasarlandı (bkz. `ai-core/README.md`).
- Uçtan uca doğrulama: backend başlatılıp `V4` migration'ı uygulandı,
  `ai_core_servis` ile giriş yapıldı, üretilen bir test videosu üzerinden
  AI Core çalıştırılıp 3 ihlal (BARET/YELEK/GOZLUK) gerçekten
  `POST /api/ihlaller` ile backend'e gönderildi, veritabanına yazıldı ve
  `admin` hesabıyla `GET /api/ihlaller` üzerinden görüntülendiği teyit
  edildi. Detay için bkz. `ILERLEME_GUNLUGU.md` Faz 7 bölümü.

Sırada Faz 8 (Entegrasyon ve Kapanış): üç katmanın uzun süreli/gerçekçi bir
akışla bir kez daha uçtan uca doğrulanması ve proje kapanış notları.
