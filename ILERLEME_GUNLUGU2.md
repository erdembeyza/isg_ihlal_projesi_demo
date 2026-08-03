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
| 🧠 **AI Core** (Python) | Kamera görüntüsünü YOLOv8/OpenCV ile analiz eder, ihlal tespit edince backend'e bildirir | ✅ Tamamlandı (Faz 7–8) — gerçek PPE modeli ile doğrulandı |
| ⚙️ **Backend** (Java/Spring Boot) | Kimlik doğrulama, ihlal kayıtlarının işlenmesi/saklanması, rol bazlı API (ISG_YONETICI / FORMEN) | ✅ Tamamlandı (Faz 2-4) — 8 endpoint de çalışıyor |
| 🖥️ **Frontend** (Angular) | Yöneticilerin ihlalleri görüntülediği, onayladığı/reddettiği web paneli | ✅ Tamamlandı (Faz 5-6) — giriş, yönetici/formen panelleri, grafik, detay modalı |

Detaylı veri modeli, DTO'lar, endpoint listesi ve bileşen hiyerarşisi için bkz.
[`tasarim_mimari.md`](./tasarim_mimari.md). Hızlı başlatma: [`README.md`](./README.md).

---

## 2) Genel İlerleme Durumu

Toplam **9 faz** (Faz 0 → Faz 8) planlanmış durumda. Her faz kendi git
branch'inde geliştirilip `--no-ff` ile `main`'e merge ediliyor ve GitHub'a
(`erdembeyza/isg_ihlal_projesi`) push ediliyor.

**İlerleme: 9 / 9 faz tamamlandı (%100)**

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
| Faz 8 | Entegrasyon ve Kapanış | ✅ Tamamlandı | `faz-8-entegrasyon-kapanis` |

---

## 3) Teknoloji Yığını

### ✅ Kurulu ve Kullanımda

| Katman | Teknoloji |
|---|---|
| Backend dili/çatısı | Java 21 (JDK 21 — Eclipse Temurin 21.0.12+8), Spring Boot 4.1.0 |
| Backend bağımlılıkları | Spring Web, Spring Data JPA, Spring Security, Validation, Flyway |
| Kimlik doğrulama | JJWT 0.13.0 (JWT üretimi/doğrulaması), BCrypt |
| Veritabanı | PostgreSQL 16 (Alpine imajı, Docker) |
| DB migration | Flyway (Spring Boot içinde otomatik; V1–V4) |
| Konteynerleştirme | Docker Desktop, docker-compose (postgres + pgAdmin servisleri) |
| DB yönetim arayüzü | pgAdmin 4 |
| Build aracı | Maven (Maven Wrapper — `mvnw`/`mvnw.cmd`) |
| Script/otomasyon | PowerShell (`scripts/flyway-migrate.ps1`, `scripts/e2e-smoke.ps1`) |
| Dosya depolama | Yerel dosya sistemi (`backend/uploads/`), `FileStorageService` üzerinden |
| Frontend çatısı | Angular 22 (standalone component mimarisi), Node.js 24.18.1, npm 11.16.0 |
| Frontend state/HTTP | Angular signals, `HttpClient` + fonksiyonel `HttpInterceptor` (JWT) |
| Grafik | Chart.js 4 + ng2-charts 10 (pasta grafik, istatistik ekranı) |
| AI / Bilgisayarlı Görü | Python 3.12, YOLOv8 Nano (ultralytics 8.3.40), OpenCV 4.10, PyTorch 2.13 |
| AI Core yardımcı kütüphaneler | requests, numpy, python-dotenv |
| PPE modeli | Construction Site Safety (Roboflow) fine-tune → `ai-core/models/ppe_yolov8n.pt` (git dışı) |

---

## 4) Kritik / Dikkat Çekici Notlar

- ⚠️ **Port 5432 çakışması (çözüldü):** Makinede Docker'dan bağımsız, native
  kurulu bir **PostgreSQL 18 Windows servisi** (`postgresql-x64-18`) 5432
  portunu işgal ediyordu; kullanıcı onayıyla Disabled yapıldı.
- 🖼️ **Foto erişimi JWT ile korunuyor:** Frontend `AuthImgDirective` ile
  blob olarak çeker.
- 🔑 **Dev/test giriş bilgileri** (yalnızca geliştirme; **üretimde
  değiştirilmeli**):

  | Kullanıcı adı | Şifre | Rol | Bölge |
  |---|---|---|---|
  | `admin` | `Admin123!` | ISG_YONETICI | Tüm fabrika |
  | `formen1` | `Formen123!` | FORMEN | Yuksek Firin-1 |
  | `ai_core_servis` | `AiCore123!` | ISG_YONETICI | Servis hesabı (`POST /api/ihlaller`) |

- 🗂️ Şema yönetimi Flyway (`ddl-auto=validate`).
- 👷 **PPE modeli:** Colab’da eğitilip `ppe_yolov8n.pt` olarak yerleştirildi;
  DEMO_MODU kapalı. Model **BARET** (`NO-Hardhat`) ve **YELEK**
  (`NO-Safety Vest`) tespit eder; sette **GOZLUK / `NO-Goggles` yok**.
- 📦 MODÜL-6 “reddedilen görseller havuzu” tasarımda ileriki fine-tune için
  bırakıldı; red işlemi `HATALI_TESPIT` + `islem_loglari` ile kayıt altında.

---

## 5) Proje kapanışı (Faz 8)

`tasarim_mimari.md` MODÜL-1…6 aksiyonları uygulandı ve
`scripts/e2e-smoke.ps1` ile uçtan uca doğrulandı:

1. Backend + AI Core servis hesabı login  
2. Gerçek PPE modeli ile video → `POST /api/ihlaller` (YELEK/BARET)  
3. Admin liste + formen (yalnızca blurlu foto, KVKK)  
4. İstatistik + reddet (`HATALI_TESPIT`)

Çalıştırma özeti: kök [`README.md`](./README.md).
