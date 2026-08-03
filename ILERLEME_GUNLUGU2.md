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
| 🧠 **AI Core** (Python) | Kamera görüntüsünü YOLOv8/OpenCV ile analiz eder, ihlal tespit edince backend'e bildirir | Planlama aşamasında (Faz 7) |
| ⚙️ **Backend** (Java/Spring Boot) | Kimlik doğrulama, ihlal kayıtlarının işlenmesi/saklanması, rol bazlı API (ISG_YONETICI / FORMEN) | ✅ Tamamlandı (Faz 2-4) — 8 endpoint de çalışıyor |
| 🖥️ **Frontend** (Angular) | Yöneticilerin ihlalleri görüntülediği, onayladığı/reddettiği web paneli | Sırada (Faz 5-6) |

Detaylı veri modeli, DTO'lar, endpoint listesi ve bileşen hiyerarşisi için bkz.
[`tasarim_mimari.md`](./tasarim_mimari.md).

---

## 2) Genel İlerleme Durumu

Toplam **9 faz** (Faz 0 → Faz 8) planlanmış durumda. Her faz kendi git
branch'inde geliştirilip `--no-ff` ile `main`'e merge ediliyor ve GitHub'a
(`erdembeyza/isg_ihlal_projesi`) push ediliyor.

**İlerleme: 5 / 9 faz tamamlandı (%56)**

| Faz | Adı | Durum | Git Branch |
|---|---|---|---|
| Faz 0 | Ortam Kurulumu | ✅ Tamamlandı | `faz-0-ortam-kurulumu` |
| Faz 1 | Veritabanı | ✅ Tamamlandı | `faz-1-veritabani` |
| Faz 2 | Backend İskeleti | ✅ Tamamlandı | `faz-2-backend-iskeleti` |
| Faz 3 | Kimlik Doğrulama (JWT Security) | ✅ Tamamlandı | `faz-3-kimlik-dogrulama` |
| Faz 4 | İhlal Servisleri (API) | ✅ Tamamlandı | `faz-4-ihlal-servisleri` |
| Faz 5 | Frontend İskeleti (Angular) | 🔄 Sırada | — *(henüz açılmadı)* |
| Faz 6 | Frontend Ekranları | ⬜ Beklemede | — |
| Faz 7 | AI Core (YOLOv8/OpenCV) | ⬜ Beklemede | — |
| Faz 8 | Entegrasyon ve Kapanış | ⬜ Beklemede | — |

> Faz 5-6 numaralandırması, proje planında Angular frontend çalışmasının iki
> alt aşamaya (iskelet + ekranlar) bölünmüş olabileceğini yansıtır; kesin
> alt-faz sınırları Faz 5 başlangıcında netleştirilecektir.

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

### ⬜ Planlanan (henüz kurulmadı)

| Katman | Teknoloji |
|---|---|
| Frontend çatısı | Angular (CLI), Node.js/nvm — Faz 5-6 |
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
- ⚠️ **Node.js / Angular CLI eksik:** Ortamda `node`, `nvm` ve `ng` komutları
  PATH üzerinden hâlâ bulunamıyor. Faz 5-6 (Angular frontend) başlamadan
  önce kurulup PATH'e eklenmesi gerekiyor.
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

## 5) Backend Tamamlandı — Sıradaki Adım: Faz 5-6 (Frontend, Angular)

Backend artık **8 endpoint'in tamamıyla** (login + 7 ihlal/kullanıcı/bölge
servisi) uçtan uca test edilmiş ve çalışır durumda — rol bazlı erişim
kontrolü (ISG_YONETICI / FORMEN) dahil. Sırada:

- Node.js (22/24) ve Angular CLI kurulumu — ortamda hâlâ PATH'te değil, bu
  faza başlamadan önce halledilmesi gerekiyor.
- `ng new` ile Angular projesinin oluşturulması.
- Giriş ekranı, yönetici paneli (tüm fabrika + istatistik grafiği + reddetme
  aksiyonu), formen paneli (kendi bölgesi + blurlu foto) bileşenleri.
- Backend'deki endpoint'lere karşılık gelen Angular servisleri (`HttpClient`
  + JWT'yi `Authorization` header'ına ekleyen bir `HttpInterceptor`).
