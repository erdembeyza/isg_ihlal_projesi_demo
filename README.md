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

- Postgres: `localhost:5432` (`isg_ihlal_db` / `isg_admin` — bkz. `docker-compose.yml`)
- pgAdmin: `http://localhost:5050`

### 2) Backend

```powershell
cd backend
.\mvnw.cmd spring-boot:run
```

API: `http://localhost:8080` — Flyway migration'ları (V1–V5) açılışta uygulanır.
Ortam değişkenleri: `backend/.env.example`.

### 3) Frontend

```powershell
cd frontend
npm install
ng serve
```

Panel: `http://localhost:4200`

| Kullanıcı | Şifre | Rol |
|---|---|---|
| `admin` | `Admin123!` | ISG_YONETICI (tüm fabrika) |
| `formen1` | `Formen123!` | FORMEN (kendi bölgesi) |

> Yalnızca geliştirme/test içindir; üretimde değiştirilmelidir.

### 4) AI Core (canlı kamera)

Üretimde AI Core **sürekli** çalışır; güvenlik kamerasının RTSP adresini
`.env` içine bir kez yazman yeter. Videoyu tek tek yüklemen gerekmez.

```powershell
cd ai-core
.\venv\Scripts\Activate.ps1
copy .env.example .env
# .env icinde: VIDEO_SOURCE=rtsp://kullanici:sifre@KAMERA_IP:554/...
python -m src.main
```

veya repo kökünden: `.\scripts\start-ai-core.ps1`

- Servis hesabı: `ai_core_servis` / `AiCore123!` (yalnızca dev)
- Çoklu kamera: `cameras.example.json` → `cameras.json`, sonra `python -m src.main --cameras cameras.json`
- Kamera yokken test: `python -m src.main --source test_videos\demo2.mp4 --loop --show`
- Panelde görünen: ihlal anı **fotoğrafı** (kaynak video siteye gitmez)

## Faz durumu

Faz 0–8 tamamlandı. Detaylar ilerleme günlüklerinde.

## Bilinen sınırlamalar (tasarıma göre / kapanış)

- **GOZLUK:** Eğitilen Construction Site Safety PPE modelinde `NO-Goggles` sınıfı yok; BARET (`NO-Hardhat`) ve YELEK (`NO-Safety Vest`) tespit edilir. Gözlük için ayrı etiketli set + fine-tune gerekir.
- **MODÜL-6 fine-tune havuzu:** Reddedilen ihlallerin orijinal fotoğrafları `backend/uploads/finetune-havuz/{tip}/` altına kopyalanır; geriye dönük senkron: `scripts/export-finetune-havuz.ps1`.
- Canlı mod: `.env` → `VIDEO_SOURCE=rtsp://...` ve `python -m src.main` (kopunca otomatik yeniden bağlanır). Geliştirmede dosya + `--loop` ile simüle edilir.
