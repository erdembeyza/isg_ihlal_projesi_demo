# İSG İhlal Tespit Projesi — İlerleme Günlüğü 3

Bu dosya, önceki ilerleme kayıtlarını özetler ve **4 Ağustos 2026** itibarıyla
yapılan yeni güncellemeleri adım adım anlatır.

| Önceki doküman | İçerik |
|---|---|
| [`ILERLEME_GUNLUGU.md`](./ILERLEME_GUNLUGU.md) | Faz 0–8 teknik günlük (detaylı) |
| [`ILERLEME_GUNLUGU2.md`](./ILERLEME_GUNLUGU2.md) | Yönetici özeti / durum panosu (3 Ağustos) |
| [`tasarim_mimari.md`](./tasarim_mimari.md) | Orijinal tasarım referansı |
| [`README.md`](./README.md) | Hızlı başlatma |

**Son güncelleme:** 4 Ağustos 2026  
**Kapsam:** Faz 0–8 kapanışı + blur kaldırma, çoklu kamera, soğuk haddehane,
personel/çözüldü, Formen panel iyileştirmeleri, Git branch stratejisi

---

## 1) Proje özeti (önceki günlüklere dayalı)

**Amaç:** Fabrika kameralarından gelen görüntüyü YOLOv8 ile analiz edip
baret/yelek (KDD) ihlallerini tespit etmek, backend’e kaydetmek ve web panelinde
yetkili personele göstermek.

**3 katman:**

| Katman | Teknoloji | Klasör |
|---|---|---|
| AI Core | Python, YOLOv8, OpenCV | `ai-core/` |
| Backend | Java 21, Spring Boot, JWT, Flyway, PostgreSQL | `backend/` |
| Frontend | Angular (standalone), Chart.js | `frontend/` |

**Faz 0–8 durumu:** Tamamlandı (%100). Her faz ayrı branch’te geliştirilip
`main`’e merge edildi. Detay: [`ILERLEME_GUNLUGU.md`](./ILERLEME_GUNLUGU.md).

| Faz | Adı | Branch |
|---|---|---|
| 0 | Ortam kurulumu | `faz-0-ortam-kurulumu` |
| 1 | Veritabanı | `faz-1-veritabani` |
| 2 | Backend iskeleti | `faz-2-backend-iskeleti` |
| 3 | JWT kimlik doğrulama | `faz-3-kimlik-dogrulama` |
| 4 | İhlal servisleri API | `faz-4-ihlal-servisleri` |
| 5 | Frontend iskeleti | `faz-5-frontend-iskeleti` |
| 6 | Frontend ekranları | `faz-6-frontend-ekranlari` |
| 7 | AI Core | `faz-7-ai-core` |
| 8 | Entegrasyon / kapanış | `faz-8-entegrasyon-kapanis` |

---

## 2) 4 Ağustos 2026 — Ne yaptık? (adım adım)

Bu bölüm, Faz 8 sonrasındaki çalışma oturumunda yapılanları sırayla anlatır.

### Adım 1 — Backend port çakışması (8080)

- Backend ikinci kez başlatılınca **Port 8080 was already in use** hatası alındı.
- Eski Java süreci `netstat` + `taskkill` ile kapatıldı.
- Ders: Aynı anda tek backend örneği çalışmalı; yeni başlatmadan önce eskiyi
  `Ctrl+C` veya PID ile sonlandır.

### Adım 2 — AI Core sanal ortam hatası

- `python -m src.main` sistem Python’u ile çalıştırılınca
  `ModuleNotFoundError: No module named 'dotenv'` alındı.
- Çözüm: önce `.\venv\Scripts\Activate.ps1`, sonra `python -m src.main ...`.

### Adım 3 — Yüz blur (KVKK) özelliğinin kaldırılması

Tasarımda orijinal + blurlu iki foto vardı; blur kaldırıldı.

**AI Core**
- `face_blur.py` silindi.
- `tools/mevcut_fotolari_yeniden_blurla.py` silindi.
- `pipeline.py` tek kanıt karesi gönderir.
- `backend_client.py` artık yalnızca `orijinalFotoBase64` yollar.

**Backend**
- `blurluFotoBase64` DTO’dan çıkarıldı.
- `Ihlal` entity’sinden `blurlu_foto_yolu` kaldırıldı.
- `FileStorageService` yalnızca orijinal foto kaydeder.
- Flyway **`V6__blur_kaldir.sql`**: kolon düşürüldü.
- Panel tüm rollerde orijinal foto gösterir.

**Önemli ders:** Kod değişince backend **yeniden başlatılmalı**. Eski süreç
ayaktayken AI Core 400 alıyordu (blur alanı hâlâ zorunluydu).

### Adım 4 — Çoklu kamera ve isimlendirme

Gerçek RTSP yerine demo için:

| Fiziksel kaynak | Sistem adı | `bolge_id` | Config |
|---|---|---|---|
| Bilgisayar webkamerası (`0`) | Veri Merkezi güvenlik kamerası | 1 | `cameras.pc.json` / `.env` |
| Telefon (IP Webcam HTTP) | 1. Sıcak Haddehane kamerası | 2 | `cameras.phone.json` |
| Tablet (IP Webcam HTTP) | 1. Soğuk Haddehane kamerası | 3 | `cameras.tablet.json` |

- Flyway **`V7__bolge_kamera_adlari.sql`**: bölge adları güncellendi
  (Veri Merkezi, 1. Sicak Haddehane).
- Flyway **`V9__soguk_haddehane_bolgesi.sql`**: 1. Soguk Haddehane eklendi.
- `cameras.json`: üç kamerayı birden listeler.
- OpenCV’de Unicode pencere adı (`—`) Windows’ta **çift boş pencere**
  açıyordu → ASCII pencere adına düzeltildi.

**Telefon / tablet bağlama**
1. Cihazda IP Webcam → Start server  
2. PC ile aynı Wi‑Fi  
3. `http://IP:8080/video` adresini ilgili JSON’a yaz  
4. Tarayıcıda IP açılmazsa AI Core da bağlanamaz (`Error -138`)

**Komutlar**

```powershell
# Sadece PC (Veri Merkezi)
python -m src.main --show

# Sadece telefon (PC kamerasına dokunmaz; --show opsiyonel)
python -m src.main --cameras cameras.phone.json

# Sadece tablet
python -m src.main --cameras cameras.tablet.json

# Üçü birden
python -m src.main --cameras cameras.json --show
```

`--show` yalnızca önizleme içindir; tespit ve panele kayıt için gerekmez.

### Adım 5 — `.env` tek kaynak kuralı

- `.env` içinde tek `VIDEO_SOURCE` vardır; hem PC hem telefon yazılamaz.
- İki/üç kamera için `cameras.json` (veya `cameras.pc.json` /
  `cameras.phone.json` / `cameras.tablet.json`) kullanılır.
- Yanlışlıkla `.env` telefona çekilirse `python -m src.main --show` telefon
  IP’sine bağlanmaya çalışır → bağlantı hatası.

### Adım 6 — Formen paneli ve personel (backend + frontend)

Flyway **`V8__personel_ve_cozuldu.sql`** ve ilgili kod:

- **Personel** entity (ad soyad, sicil no, departman).
- İhlal durumuna **`COZULDU`** eklendi; `POST .../coz` ile işaretleme.
- Formen panelinde:
  - KPI kartları (aktif / bugünkü / bölge risk durumu)
  - “Çözüldü işaretle”
  - CSV/Excel tarzı dışa aktarma
  - Personel bazlı ihlal özeti

### Adım 7 — Git: kategoriye göre branch ve push

`main`’e doğrudan basılmadı. Stacked feature branch’ler oluşturulup GitHub’a
push edildi (`erdembeyza/isg_ihlal_projesi`):

| Sıra | Branch | Ne içerir |
|---|---|---|
| 1 | `1-soguk-haddehane` | V6–V9 migration’lar, `cameras.json`, tablet config, soğuk haddehane bölgesi |
| 2 | `blur-kaldir` | AI Core blur kaldırma |
| 3 | `backend-personel-cozuldu` | Backend blur API + personel + COZULDU |
| 4 | `formen-panel` | Formen KPI / çözüldü / CSV / personel UI |
| 5 | `kamera-ayirma` | `cameras.pc.json` / `cameras.phone.json` + README |

**Önerilen merge sırası:** yukarıdaki sıra (1 → 5).  
Ortadan bir branch’i atlamak bağımlılıkları bozabilir (ör. frontend’siz
backend veya blur’suz AI + eski backend).

PR örnekleri:
- https://github.com/erdembeyza/isg_ihlal_projesi/pull/new/1-soguk-haddehane
- https://github.com/erdembeyza/isg_ihlal_projesi/pull/new/blur-kaldir
- https://github.com/erdembeyza/isg_ihlal_projesi/pull/new/backend-personel-cozuldu
- https://github.com/erdembeyza/isg_ihlal_projesi/pull/new/formen-panel
- https://github.com/erdembeyza/isg_ihlal_projesi/pull/new/kamera-ayirma

---

## 3) Flyway migration özeti (güncel)

| Versiyon | Dosya | Açıklama |
|---|---|---|
| V1–V5 | (Faz 1–8) | Şema, seed, bölgeler, AI Core hesabı/rolü |
| V6 | `V6__blur_kaldir.sql` | `blurlu_foto_yolu` kolonunu düşürür |
| V7 | `V7__bolge_kamera_adlari.sql` | Veri Merkezi / 1. Sicak Haddehane adları |
| V8 | `V8__personel_ve_cozuldu.sql` | Personel + çözüldü alanları |
| V9 | `V9__soguk_haddehane_bolgesi.sql` | 1. Soguk Haddehane (`bolge_id` ≈ 3) |

Backend her açılışta eksik migration’ları uygular.

---

## 4) Çalıştırma kontrol listesi (güncel)

1. `docker compose up -d` (Postgres)  
2. Backend: `cd backend` → `.\mvnw.cmd spring-boot:run`  
3. Frontend: `cd frontend` → `ng serve` → http://localhost:4200  
4. AI Core (venv aktif):
   - PC: `python -m src.main --show`
   - Telefon: `python -m src.main --cameras cameras.phone.json`
   - Hepsi: `python -m src.main --cameras cameras.json`

| Kullanıcı | Şifre | Rol |
|---|---|---|
| `admin` | `Admin123!` | ISG_YONETICI |
| `formen1` | `Formen123!` | FORMEN |
| `ai_core_servis` | `AiCore123!` | AI Core servis hesabı |

---

## 5) Bilinen sınırlamalar / dersler

- **GOZLUK:** PPE modelinde `NO-Goggles` yok; BARET ve YELEK çalışır.
- **8080 / 5432 çakışması:** Eski süreç veya native Postgres portu kapalı olmalı.
- **Telefon IP’si değişir:** Wi‑Fi değişince `cameras.*.json` güncellenmeli.
- **Blur sonrası 400:** Backend eski kodla kalırsa AI Core kayıt atamaz → restart.
- **`--show` zorunlu değil:** Arka planda tespit + panel kaydı yeter.
- **`test_videos/`** büyük dosyalar / ekran görüntüleri genelde git’e
  eklenmedi.

---

## 6) Önceki günlüklere referans

- Faz 0–8’in komut, doğrulama ve dosya listeleri için:  
  [`ILERLEME_GUNLUGU.md`](./ILERLEME_GUNLUGU.md)
- Kısa yönetici özeti (3 Ağustos):  
  [`ILERLEME_GUNLUGU2.md`](./ILERLEME_GUNLUGU2.md)

Bu dosya (**Günlük 3**), o iki kaydı geçersiz kılmaz; üzerine **yeni dönem
güncellemelerini** ekler.
