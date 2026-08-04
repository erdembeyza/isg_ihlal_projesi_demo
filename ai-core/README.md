# AI Core — Canlı güvenlik kamerası İSG tespit servisi

MODÜL-1: kamera görüntüsünü (RTSP) YOLOv8 ile sürekli analiz eder; baret/yelek
ihlalini tespit edince kanıt **fotoğrafını** backend’e
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

### Çoklu kamera (PC + telefon)

`cameras.json` hazır: bilgisayar kamerası = Veri Merkezi, telefon = 1. Sicak Haddehane.

```powershell
copy cameras.example.json cameras.json
# cameras.json icinde TELEFON_IP yerine telefonunun Wi-Fi IP'sini yaz
python -m src.main --cameras cameras.json --show
```

**Telefonu bağlama (Android — IP Webcam):**

1. Telefona [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) yükle.
2. Telefon ile bilgisayar **aynı Wi‑Fi**’de olsun.
3. Uygulamada **Start server**’a bas.
4. Ekranda görünen adresi not al (ör. `http://192.168.1.34:8080`).
5. `cameras.json` içinde `TELEFON_IP` yerine o IP’yi yaz:
   `"video_source": "http://192.168.1.34:8080/video"`
6. AI Core’u `--cameras cameras.json` ile başlat.

iPhone için benzer uygulama (ör. **IP Camera** / **EpocCam**) veya bilgisayara DroidCam/Iriun ile sanal kamera da kullanılabilir; OpenCV `http://.../video` veya `rtsp://...` bekler.

Her kayıt kendi `bolge_id` ile ayrı thread’de izlenir; panelde ihlaller ilgili bölge adıyla görünür.

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
| `backend_client.py` | JWT + POST ihlal |

## Bilinen sınırlamalar

- Kişi ↔ KDD eşlemesi merkez mesafesine göre.
- Cooldown ihlal tipi bazlıdır (kişi bazlı değil).
- Web sitesinde video oynatma yoktur; yalnızca ihlal anı fotoğrafı vardır.
