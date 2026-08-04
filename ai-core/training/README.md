# PPE Model Fine-Tune Rehberi

Mevcut model: `ai-core/models/ppe_yolov8n.pt` (25 sinif)

Bu rehber, az sayida yeni gorselle modeli **sifirdan egitmek yerine**
mevcut bilgiyi koruyarak guncellemek (fine-tune) icin adim adim yol gosterir.

---

## Onemli: Sinif isimleri `baret` / `yelek` DEGIL

Projede kullanilan model, Roboflow **Construction Site Safety** veri setinden
turedilmistir. Etiketler Turkce degil, Ingilizce ve **tam olarak su isimlerle**
yazilmalidir:

| Indeks | Sinif adi | Projedeki anlami |
|--------|-----------|------------------|
| 5 | `NO-Hardhat` | Baret yok (BARET ihlali) |
| 7 | `NO-Safety Vest` | Yelek yok (YELEK ihlali) |
| 8 | `Person` | Kisi |
| 2 | `Hardhat` | Baret var |
| 11 | `Safety Vest` | Yelek var |

Tam listeyi gormek icin:

```powershell
cd ai-core
.\venv\Scripts\Activate.ps1
python training\siniflari_goster.py
```

Roboflow'ta `baret` veya `NO-hardhat` (kucuk harf) yazarsaniz model
bunu yeni bir nesne sanir ve bozulur.

---

## Adim 1 — Gorselleri topla

Projede iki kaynak var:

1. **Test gorselleri:** `ai-core/test_videos/` (or. `kamera_ekran_goruntusu.jpg`)
2. **Fine-tune havuzu:** Reddedilen ihlal fotolari
   (`backend/uploads/finetune-havuz/{BARET|YELEK|GOZLUK}/`)

Havuzu doldurmak icin (backend ayaktayken):

```powershell
.\scripts\export-finetune-havuz.ps1
```

Gorselleri Roboflow yuklemesi icin tek klasore toplamak:

```powershell
cd ai-core
.\training\roboflowa_hazirla.ps1
# Cikti: ai-core/training/roboflow_yukleme/
```

---

## Adim 2 — Roboflow'ta etiketle

1. [roboflow.com](https://roboflow.com) → yeni proje (Object Detection)
2. `training/roboflow_yukleme/` klasorundeki gorselleri yukle
3. Her gorselde eksik ekipmani kutu icine al:
   - Baret yoksa → **`NO-Hardhat`**
   - Yelek yoksa → **`NO-Safety Vest`**
   - Kisi varsa → **`Person`**
4. **Train/Valid bol** (az veride %80 train / %20 valid yeterli)
5. **Generate → YOLOv8 → Download zip**

---

## Adim 3 — Zip'i projeye cikart

Indirdigin `.zip` dosyasini su klasore cikart:

```
ai-core/training/yeni_veri_seti/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── data.yaml
```

`data.yaml` icindeki yollarin dogru oldugundan emin ol. Ornek:

```yaml
path: .
train: train/images
val: valid/images

nc: 25
names:
  - Excavator
  - Gloves
  - Hardhat
  # ... (tam liste icin data.yaml.example dosyasina bakin)
```

Roboflow'un indirdigi `data.yaml` genelde farkli sinif sayisi icerir.
**Mutlaka** `training/data.yaml.example` ile karsilastirin ve
`names` listesini mevcut modelle birebir eslestirin.

---

## Adim 4 — Fine-tune egitimini baslat

```powershell
cd ai-core
.\venv\Scripts\Activate.ps1
python training\egitim_scripti.py
```

Script su parametreleri kullanir (az veri + mevcut agirlik koruma):

| Parametre | Deger | Neden |
|-----------|-------|-------|
| `lr0` | 0.0001 | Normal 0.01 yerine cok dusuk; eski bilgiyi bozmaz |
| `freeze` | 10 | Ilk katmanlar dondurulur |
| `epochs` | 30 | Az veride overfitting riski |
| `batch` | 8 | VRAM dostu |

Egitim ciktisi:

```
ai-core/runs/detect/isg_guncellenmis_model/weights/best.pt
```

---

## Adim 5 — Yeni modeli uretime al

```powershell
cd ai-core
.\training\modeli_yerlestir.ps1
```

Bu komut `best.pt` dosyasini `models/ppe_yolov8n.pt` konumuna kopyalar
(eski modeli `.yedek` olarak saklar).

AI Core'u yeniden baslatin; `.env` icinde `YOLO_MODEL_PATH=models/ppe_yolov8n.pt`
zaten varsayilan.

---

## Klasor yapisi (ozet)

```
ai-core/
├── models/
│   └── ppe_yolov8n.pt              # Mevcut / guncellenmis uretim modeli
├── training/
│   ├── egitim_scripti.py           # Fine-tune baslat
│   ├── siniflari_goster.py         # Sinif listesini yazdir
│   ├── roboflowa_hazirla.ps1       # Gorselleri topla
│   ├── modeli_yerlestir.ps1        # best.pt → models/
│   ├── data.yaml.example           # Ornek sinif listesi
│   ├── roboflow_yukleme/           # Roboflow'a yuklenecek gorseller
│   └── yeni_veri_seti/             # Roboflow'tan indirilen veri
└── runs/detect/isg_guncellenmis_model/weights/best.pt
```

---

## Sik yapilan hatalar

1. **Turkce etiket** (`baret`, `yelek`) → Model bozulur
2. **Yanlis sinif sayisi** (`nc: 2`) → Mevcut model 25 sinif; `data.yaml` da 25 olmali
3. **Cok yuksek ogrenme orani** → Eski bilgi silinir; `lr0=0.0001` kullanin
4. **Cok fazla epoch** → Overfitting; 30 yeterli
5. **Egitim verisi yokken script calistirmak** → Once Roboflow adimlarini tamamlayin
