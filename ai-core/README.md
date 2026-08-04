# AI Core — Canlı güvenlik kamerası İSG tespit servisi

MODÜL-1: kamera görüntüsünü (RTSP) YOLOv8 ile sürekli analiz eder; baret/yelek
ihlalini tespit edince kanıt **fotoğrafını** (orijinal + yüzü blurlu) backend’e
`POST /api/ihlaller` ile gönderir. Web paneli bu fotoğrafları anlık listeler.

**Üretim modu:** Kamerayı bir kez `.env` (veya `cameras.json`) içine yazarsın;
AI Core açık kaldığı sürece **sürekli izler**. Videoyu tek tek elle yüklemen
gerekmez.

## Kurulum

```powershell
cd ai-core
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

`.env` içinde özellikle şunları düzenle:

| Alan | Anlamı |
|---|---|
| `VIDEO_SOURCE` | Kamera RTSP adresi (`rtsp://user:pass@IP:554/...`) |
| `BOLGE_ID` | Bu kameranın `bolgeler.id` değeri |
| `BACKEND_BASE_URL` | Spring Boot adresi |

## Canlı kamera

### Bilgisayar webkami (şimdilik önerilen)

Gerçek güvenlik kameran yoksa laptop/PC kamerası güvenlik kamerası gibi
sürekli izlenir:

1. Backend + Postgres ayakta olsun.
2. `.env` içinde: `VIDEO_SOURCE=0` (veya `webcam`)
3. Başlat:

```powershell
cd ai-core
.\venv\Scripts\Activate.ps1
python -m src.main --show
```

Windows’ta ilk seferde kamera izni isteyebilir — İzin Ver.

### Gerçek RTSP güvenlik kamerası

`.env` → `VIDEO_SOURCE=rtsp://kullanici:sifre@IP:554/...` sonra `python -m src.main`

- Akış koparsa otomatik yeniden bağlanır.
- İhlal olunca panelde **fotoğraf** görünür.
- Durdurmak: `Ctrl+C` veya pencerede `q`.

### Çoklu kamera

`cameras.example.json` dosyasını kopyalayıp RTSP adreslerini doldur:

```powershell
copy cameras.example.json cameras.json
python -m src.main --cameras cameras.json
```

Her kayıt kendi `bolge_id` ile ayrı thread’de izlenir.

## Kamera yokken geliştirme (simulasyon)

Yerel videoyu **döngüde** oynatmak = canlı kamera gibi davranır:

```powershell
python -m src.main --source test_videos/demo2.mp4 --loop --show
```

`--loop` olmadan dosya bitince süreç durur. RTSP’de `--loop` gerekmez.

Kuru kalibrasyon (backend’e göndermez):

```powershell
python -m src.main --source test_videos/demo2.mp4 --loop --dry-run --show
```

## PPE modeli

`models/ppe_yolov8n.pt` yoksa DEMO_MODU’na düşer (gerçek üretim tespiti değil).
GOZLUK sınıfı mevcut eğitimde yoktur (BARET / YELEK çalışır).

## Mimari

| Dosya | Sorumluluk |
|---|---|
| `config.py` | `.env` + `cameras.json` |
| `stream.py` | RTSP açma, TCP, buffer, yeniden bağlanma |
| `pipeline.py` | Tespit döngüsü, cooldown, bildirim |
| `main.py` | CLI / çoklu kamera thread’leri |
| `ppe_detector.py` | YOLOv8 |
| `face_blur.py` | KVKK yüz bulanıklaştırma |
| `backend_client.py` | JWT + POST ihlal |

## Bilinen sınırlamalar

- Kişi ↔ KDD eşlemesi merkez mesafesine göre.
- Cooldown ihlal tipi bazlıdır (kişi bazlı değil).
- Web sitesinde video oynatma yoktur; yalnızca ihlal anı fotoğrafı vardır.
