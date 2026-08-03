# İSG Kural İhlal Tespit ve Uyarı Sistemi

Erdemir üretim sahalarında baret, yelek veya gözlük (KDD) takmayan personeli
kamera görüntüsünden gerçek zamanlı tespit eden, kaydeden ve yetkili personele
web paneli üzerinden raporlayan sistem.

**Tek referans tasarım:** [`tasarim_mimari.md`](./tasarim_mimari.md)  
**İlerleme:** [`ILERLEME_GUNLUGU.md`](./ILERLEME_GUNLUGU.md) · özet: [`ILERLEME_GUNLUGU2.md`](./ILERLEME_GUNLUGU2.md)

## Mimari (3 katman)

| Katman | Teknoloji | Klasör | Tasarım modülü |
|---|---|---|---|
| AI Core | Python, YOLOv8 Nano, OpenCV | `ai-core/` | MODÜL-1 |
| Backend | Java 21, Spring Boot, JWT, Flyway, PostgreSQL | `backend/` | MODÜL-2, MODÜL-3, MODÜL-6 |
| Frontend | Angular (standalone), Chart.js | `frontend/` | MODÜL-4, MODÜL-5 (+ bileşenler) |

## Hızlı başlatma (uçtan uca)

Üç süreç ayrı terminallerde çalışır. Sıra: veritabanı → backend → (isteğe bağlı) frontend → AI Core.

### 1) PostgreSQL + pgAdmin

```powershell
docker compose up -d
```

- Postgres: `localhost:5432` (`isg_db` / `isg_admin` — bkz. `docker-compose.yml`)
- pgAdmin: `http://localhost:5050`

### 2) Backend

```powershell
cd backend
.\mvnw.cmd spring-boot:run
```

API: `http://localhost:8080` — Flyway migration'ları (V1–V4) açılışta uygulanır.

### 3) Frontend

```powershell
cd frontend
npm install
ng serve
```

Panel: `http://localhost:4200`

| Kullanıcı | Şifre | Rol |
|---|---|---|
| `admin` | `Admin123!` | ISG_YONETICI (tüm fabrika, orijinal foto) |
| `formen1` | `Formen123!` | FORMEN (kendi bölgesi, blurlu foto) |

> Yalnızca geliştirme/test içindir; üretimde değiştirilmelidir.

### 4) AI Core

```powershell
cd ai-core
.\venv\Scripts\Activate.ps1   # yoksa: python -m venv venv && pip install -r requirements.txt
copy .env.example .env        # bir kez; gerekirse VIDEO_SOURCE / BOLGE_ID düzenleyin
python -m src.main --source test_videos\demo.mp4
```

- Servis hesabı: `ai_core_servis` / `AiCore123!` (V4 migration — yalnızca dev)
- Gerçek PPE modeli: `ai-core/models/ppe_yolov8n.pt` (git'e alınmaz; Colab/eğitim sonrası buraya konur)
- Offline kalibrasyon: `python -m src.main --source test_videos\demo.mp4 --dry-run --show`
- Kaggle İSG videoları: dosyayı `ai-core/test_videos/` altına koyup `--source` ile verin (bkz. `tasarim_mimari.md` test notu)

## Faz durumu

Faz 0–8 tamamlandı. Detaylar ilerleme günlüklerinde.

## Bilinen sınırlamalar (tasarıma göre / kapanış)

- **GOZLUK:** Eğitilen Construction Site Safety PPE modelinde `NO-Goggles` sınıfı yok; BARET (`NO-Hardhat`) ve YELEK (`NO-Safety Vest`) tespit edilir. Gözlük için ayrı etiketli set + fine-tune gerekir.
- **MODÜL-6 “reddedilen görseller havuzu”:** Tasarımda “ileriki fazlarda fine-tuning için işaretlenir” denmiştir; red işlemi `HATALI_TESPIT` + `islem_loglari` ile kayıt altındadır, ayrı bir export klasörü henüz yoktur.
- Canlı RTSP yerine geliştirmede yerel/Kaggle videosu kullanılır; `.env` içinde `VIDEO_SOURCE=rtsp://...` ile canlı akışa geçilebilir.
