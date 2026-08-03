# AI Core — İSG Kural İhlal Tespit Servisi (Faz 7)

MODÜL-1 (`tasarim_mimari.md`): kamera görüntüsünü YOLOv8 Nano ile analiz
eden, KDD (baret/yelek/gözlük) ihlallerini tespit edip kanıt fotoğraflarını
(orijinal + yüzü blurlanmış) `POST /api/ihlaller` ile Java backend'ine
bildiren Python servisi.

## Kurulum

```powershell
cd ai-core
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

`.env` dosyasındaki alanları kendi ortamınıza göre düzenleyin (özellikle
`BACKEND_BASE_URL`, `VIDEO_SOURCE`, `BOLGE_ID`). Varsayılan
`AI_CORE_KULLANICI_ADI`/`AI_CORE_SIFRE` değerleri, backend'deki
`V4__ai_core_servis_hesabi.sql` migration'ı ile eklenen **dev/test amaçlı**
servis hesabıyla eşleşir.

## Çalıştırma

```powershell
# .env'deki VIDEO_SOURCE (RTSP akışı ya da dosya) ile canlı mod
python -m src.main

# Yerel bir video ile, backend'e HİÇBİR ŞEY GÖNDERMEDEN kalibrasyon
python -m src.main --source test_videos/demo.mp4 --dry-run --show

# Test videosunu sonsuz döngüde oynatarak canlı akışı simüle et
python -m src.main --source test_videos/demo.mp4 --loop
```

CLI bayrakları: `--source`, `--dry-run` (backend'e göndermez, yalnızca
loglar), `--debug-output <klasör>` (kuru çalıştırmada kareleri diske
kaydeder), `--show` (tespit kutularını pencerede gösterir), `--loop`
(video dosyasını başa sararak tekrar oynatır), `--verbose`.

## PPE modeli

`.env` içindeki `YOLO_MODEL_PATH` (varsayılan `models/ppe_yolov8n.pt`)
Construction Site Safety (Roboflow) ile fine-tune edilmiş YOLOv8n ağırlığını
bekler. Bu dosya `.gitignore`'dadır; Colab'da üretilen `best.pt` buraya
kopyalanır.

Beklenen ihlal sınıfları (`src/ppe_detector.py` → `SINIF_TO_IHLAL_TIPI`):

| Model sınıfı | Sistem ihlal tipi |
|---|---|
| `NO-Hardhat` / `NO-Helmet` | BARET |
| `NO-Safety Vest` / `NO-Vest` | YELEK |
| `NO-Goggles` / `NO-Glasses` | GOZLUK |

Mevcut Construction Site Safety eğitiminde **`NO-Goggles` yoktur**; GOZLUK
tespiti için gözlük etiketli bir setle ek fine-tune gerekir. Kişi sınıfı
hem `person` (COCO) hem `Person` (Roboflow) olarak tanınır.

Dosya yoksa sistem COCO `yolov8n.pt`'e düşüp **DEMO_MODU**'na geçer (yalnızca
geliştirme: her kişi tüm ihlal tipleriyle işaretlenir — gerçek tespit değil).

## Test videosu üretme (Kaggle olmadan hızlı kalibrasyon)

Gerçek Kaggle İSG ihlali videolarına erişim/hesap gerektirmeden, DEMO_MODU
boru hattını hızlıca doğrulamak için `ultralytics` paketiyle birlikte gelen
(içinde gerçek insanlar bulunan) örnek görselden küçük bir test videosu
üretilebilir:

```powershell
python tools/test_video_uret.py --cikti test_videos/demo.mp4 --kare-sayisi 30
python -m src.main --source test_videos/demo.mp4 --dry-run --debug-output debug_output
```

Gerçek kullanımda bu, Kaggle'daki açık kaynak İSG ihlali videolarıyla
(`test_videos/` altına indirilip) değiştirilmelidir — bkz.
`tasarim_mimari.md` "Test ve entegrasyon" notu.

## Mimari (src/)

| Dosya | Sorumluluk |
|---|---|
| `config.py` | `.env` okuma, tip dönüşümü, yol çözümleme |
| `auth_client.py` | Backend'e `/api/auth/login` ile giriş, JWT önbellekleme/yenileme |
| `backend_client.py` | Kareyi base64 JPEG'e çevirme, `IhlalKayitRequestDTO` ile `POST /api/ihlaller`, 401'de otomatik yeniden giriş |
| `face_blur.py` | Haar Cascade ile yüz tespiti + `cv2.GaussianBlur`; yüz bulunamazsa güvenlik ağı olarak kişi kutusunun üst çeyreği blurlanır |
| `ppe_detector.py` | YOLOv8 modelini yükler, sınıf → ihlal tipi eşlemesi yapar, PPE modeli yoksa DEMO_MODU'na düşer |
| `pipeline.py` | Video okuma döngüsü, frame atlama, cooldown (spam engelleme), kanıt üretimi ve backend'e bildirim |
| `main.py` | CLI giriş noktası (`--source`, `--dry-run`, `--show`, `--loop`, `--debug-output`) |

## Bilinen sınırlamalar

- Kişi ↔ KDD-eksik kutusu eşleştirmesi merkez mesafesine göre yapılır
  (basit ama kalabalık sahnelerde hatalı eşleşme riski taşır); çoklu nesne
  takibi (ör. ByteTrack) kapsam dışı bırakılmıştır.
- Cooldown (varsayılan 30 sn) ihlal tipi bazlıdır, kişi bazlı değildir;
  aynı anda birden fazla farklı kişi aynı ihlal tipini tetiklerse ilk
  bildirimden sonraki cooldown süresince diğerleri raporlanmaz.
