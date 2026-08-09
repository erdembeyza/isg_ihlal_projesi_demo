# İSG Kural İhlal Tespit ve Uyarı Sistemi — Öğrenci Anlatım Dokümanı

Bu dosya, projeyi **hiç bilmeyen bir öğrenciye** anlatmak için yazılmıştır.  
Amaç: “Ne yaptık?”, “Neden yaptık?”, “Hangi katmanda ne var?” ve “Bir ihlal nasıl ekrana düşüyor?” sorularını sade dille cevaplamak.

Daha teknik / kısa referanslar:

| Dosya | Ne işe yarar? |
|---|---|
| [`README.md`](./README.md) | Projeyi ayağa kaldırma (hızlı başlangıç) |
| [`tasarim_mimari.md`](./tasarim_mimari.md) | Orijinal tasarım (tablolar, DTO, modüller) |
| [`ILERLEME_GUNLUGU.md`](./ILERLEME_GUNLUGU.md) | Faz 0–8 teknik günlük |
| [`ILERLEME_GUNLUGU2.md`](./ILERLEME_GUNLUGU2.md) | Kısa durum özeti |
| [`ILERLEME_GUNLUGU3.md`](./ILERLEME_GUNLUGU3.md) | Faz 8 sonrası ek geliştirmeler |

---

## 1) Proje ne?

### 1.1 Tek cümlelik özet

Bu proje; fabrika / şantiye **güvenlik kameralarından** gelen görüntüyü yapay zekâ ile izleyerek, personelin **baret** veya **yelek** gibi kişisel koruyucu donanımı (KKD / KDD) takmadığı anları otomatik tespit eden, kaydeden ve yetkili personele **web paneli** üzerinden gösteren bir **İş Sağlığı ve Güvenliği (İSG)** sistemidir.

### 1.2 Problem neydi?

Demir-çelik üretimi gibi yüksek riskli ortamlarda (sıcak haddehane, soğuk haddehane, yüksek fırın vb.):

- Kameralar zaten vardır; ama bir insanın 7/24 ekran izlemesi zordur.
- İhlal geç fark edilirse müdahale de geç kalır.
- “Kim, nerede, ne zaman, hangi ekipmanı takmamış?” sorusunun **kanıtlı kaydı** çoğu zaman eksik kalır.

Yani problem sadece “ihlali görmek” değil; **otomatik, hızlı, kayıtlı ve yetki kontrollü** hale getirmekti.

### 1.3 Çözüm neydi?

Yeni kamera almak yerine (sıfır donanım maliyeti hedefi):

1. Mevcut kameradan görüntü alınır (RTSP, webkamera, telefon IP Webcam, test videosu).
2. **AI Core** (Python + YOLOv8) kareleri analiz eder.
3. İhlal varsa kanıt **fotoğrafı** backend’e gönderilir.
4. **Backend** (Java Spring Boot) kaydı PostgreSQL’e yazar.
5. **Frontend** (Angular) panelde yönetici / formen / izleyici rolüne göre gösterir.

### 1.4 Tespit edilen ihlal tipleri

| Tip | Anlamı | Modelde karşılığı |
|---|---|---|
| **BARET** | Baret takılmamış | `NO-Hardhat` |
| **YELEK** | Güvenlik yeleği yok | `NO-Safety Vest` |
| **GOZLUK** | Gözlük yok (tasarımda var) | `NO-Goggles` — mevcut eğitim setinde sınıf yok; ileride fine-tune gerekir |

Önemli: Panelde “video izleme” yoktur. Sistem, ihlal anının **fotoğrafını** kaydeder ve gösterir.

---

## 2) Büyük resim: 3 katmanlı mimari

Projeyi bir sandviç gibi düşün:

```text
┌─────────────────────────────────────────────────────────┐
│  FRONTEND (Angular)                                     │
│  Kullanıcı paneli: giriş, listeler, grafikler, aksiyon  │
└──────────────────────────▲──────────────────────────────┘
                           │ HTTP + JWT
┌──────────────────────────┴──────────────────────────────┐
│  BACKEND (Java Spring Boot + PostgreSQL)                │
│  API, güvenlik, dosya saklama, istatistik, rapor         │
└──────────────────────────▲──────────────────────────────┘
                           │ POST /api/ihlaller (JWT)
┌──────────────────────────┴──────────────────────────────┐
│  AI CORE (Python + YOLOv8 + OpenCV)                     │
│  Kamerayı izler, ihlali bulur, fotoğraf gönderir         │
└─────────────────────────────────────────────────────────┘
```

| Katman | Klasör | Teknoloji | Basit görevi |
|---|---|---|---|
| **AI Core** | `ai-core/` | Python, OpenCV, Ultralytics YOLOv8 | Görüntüyü okur, nesne/ihlal bulur |
| **Backend** | `backend/` | Java 21, Spring Boot, JWT, Flyway, PostgreSQL | Veriyi saklar, yetkiyi kontrol eder, API sunar |
| **Frontend** | `frontend/` | Angular (standalone), Chart.js | İnsanların ekrandan iş yapmasını sağlar |

Bunların yanında:

- `docker-compose.yml` → PostgreSQL + pgAdmin
- `scripts/` → yardımcı PowerShell script’leri
- `tasarim_mimari.md` → “ne yapılacak”ın resmi planı

---

## 3) Projeyi nasıl yaptık? (Faz faz hikâye)

Geliştirme rastgele yapılmadı. Önce tasarım yazıldı (`tasarim_mimari.md`), sonra **Faz 0 → Faz 8** ile adım adım kodlandı. Her faz genelde kendi Git branch’inde gelişti, bitince `main`’e merge edildi.

### Faz 0 — Ortam kurulumu

- Proje klasörleri açıldı: `ai-core/`, `backend/`, `frontend/`
- `.gitignore` yazıldı (büyük model dosyaları, `node_modules`, `venv` vb. git’e girmesin diye)
- `docker-compose.yml` ile veritabanı altyapısı hazırlandı
- AI Core için `requirements.txt` ve `.env.example` konuldu

**Öğrenci diliyle:** Ev inşa etmeden önce arsa ve elektrik hattını hazırlamak.

### Faz 1 — Veritabanı

- PostgreSQL Docker’da ayağa kalktı
- Flyway migration’ları yazıldı:
  - `V1__init.sql` → tablolar ve kısıtlar
  - `V2__seed.sql` → örnek bölgeler, ihlal tipleri, admin/formen kullanıcıları
- Şifreler düz metin değil, **BCrypt hash** olarak saklandı

**Öğrenci diliyle:** Verilerin kalıcı “defterini” oluşturduk.

### Faz 2 — Backend iskeleti

- Spring Boot projesi kuruldu
- Entity + Repository katmanı yazıldı (`Bolge`, `Kullanici`, `Ihlal`, …)
- Backend Postgres’e bağlandı

### Faz 3 — Kimlik doğrulama (JWT)

- Login endpoint’i (`POST /api/auth/login`)
- JWT üretimi / doğrulama
- Spring Security filtreleri
- Rol kontrolü: yetkisiz istek → **403 Forbidden**

### Faz 4 — İhlal servisleri

- AI Core’un ihlal göndereceği `POST /api/ihlaller`
- Panelin listeleyeceği `GET /api/ihlaller`
- İstatistik, reddetme, dosya saklama (`FileStorageService`)

### Faz 5 — Frontend iskeleti

- Angular projesi
- `AuthService`, JWT interceptor, guard’lar
- Login + boş dashboard iskeletleri

### Faz 6 — Frontend ekranları

- İhlal listesi, pasta grafik, detay modalı
- Yönetici ve formen panellerinin dolu hali
- Fotoğrafların JWT ile güvenli yüklenmesi (`AuthImgDirective`)

### Faz 7 — AI Core

- Kamera/video okuma
- YOLOv8 ile PPE tespiti
- Backend’e login + ihlal POST
- Test videosu / demo modu

### Faz 8 — Entegrasyon ve kapanış

- Uçtan uca smoke test (`scripts/e2e-smoke.ps1`)
- README ve kapanış notları
- Gerçek PPE modeli ile doğrulama

### Faz 8 sonrası (günlük 3 ve sonrası)

Bunlar “bitmiş proje üzerine eklenen iyileştirmeler”:

- Çoklu kamera (PC + telefon + tablet)
- Bölge adları (Veri Merkezi, Sıcak/Soğuk Haddehane, Yüksek Fırın A/B)
- Personel / “Çözüldü” durumu
- Kamera heartbeat (kamera online mi?)
- Görüntüleyici (salt okunur) rolü
- Profil, kullanıcı yönetimi, denetim günlüğü, raporlar
- Fine-tune havuzu (yanlış tespitlerden model iyileştirme verisi)

---

## 4) Uçtan uca akış (bir ihlalin hayatı)

Bir ihlalin sistemdeki yolculuğu:

```text
1) Kamera karesi gelir
        ↓
2) AI Core her N karede YOLOv8 çalıştırır
        ↓
3) "Person" + "NO-Hardhat" / "NO-Safety Vest" bulunur
        ↓
4) IoU tracker: aynı kişi üzerinde ihlal süresi birikir
        ↓
5) Minimum süre eşiği aşılırsa (yanlış alarm azaltmak için)
        ↓
6) Kanıt karesi çizilir (kırmızı kutu), gerekirse yüz blur uygulanır
        ↓
7) AI Core JWT ile login olur (ai_core_servis hesabı)
        ↓
8) POST /api/ihlaller  →  foto base64 + bölge + tip + zaman
        ↓
9) Backend fotoğrafı diske yazar, DB'ye kayıt ekler (durum: AKTIF)
        ↓
10) Frontend paneli listeyi çeker → kullanıcı görür
        ↓
11a) Formen: "Çözüldü" işaretler
  veya
11b) Yönetici: "Hatalı tespit" der → istatistikten düşer + fine-tune havuzuna kopyalanabilir
```

Bu akış projenin kalbidir. Üç katman birbirinden bağımsız çalışabilir ama **birlikte bir ürün** olur.

---

## 5) AI Core — Yapay zekâ görüntü işleme katmanı

Klasör: `ai-core/`  
Tasarımda adı: **MODÜL-1**

### 5.1 AI Core ne yapar? (çok basit)

AI Core bir “göz” gibidir:

- Kamerayı sürekli izler
- “Bu karede baret/yelek ihlali var mı?” diye bakar
- Varsa fotoğraf çeker ve backend’e “bak, burada ihlal var” diye haber verir

Web sitesi **yapmaz**. Veritabanına **doğrudan yazmaz**. Sadece tespit + bildirim yapar.

### 5.2 Neden Python?

Bilgisayarlı görü ekosistemi (OpenCV, YOLO/Ultralytics, NumPy) Python’da çok olgun.  
Kamera karesi işlemek ve modeli çalıştırmak için pratik seçimdir.

### 5.3 Kullanılan teknolojiler

| Araç | Ne işe yarar? |
|---|---|
| **OpenCV (`cv2`)** | Videoyu/kamerayı açar, kare okur, çizim yapar, pencere gösterir |
| **YOLOv8 Nano (Ultralytics)** | Nesne tespiti: kişi, baret yok, yelek yok vb. |
| **PyTorch** | YOLO modelinin altında çalışan derin öğrenme motoru |
| **requests** | Backend’e HTTP istekleri |
| **python-dotenv** | `.env` ayarlarını okur |
| **NumPy** | Görüntü matris işlemleri |

Model dosyası genellikle: `ai-core/models/ppe_yolov8n.pt`  
Bu dosya büyüktür; genelde git’e konmaz. Yoksa sistem **DEMO_MODU**’na düşer (sadece “person” görür; gerçek PPE ihlali üretmez).

### 5.4 Önemli dosyalar

| Dosya | Görevi |
|---|---|
| `src/main.py` | Programın giriş noktası; CLI argümanları; çoklu kamera thread’leri |
| `src/config.py` | `.env` ve `cameras.json` ayarlarını okur |
| `src/stream.py` | RTSP/HTTP/webcam akışını açar; kopunca yeniden bağlanır |
| `src/ppe_detector.py` | YOLO modeli + sınıf → BARET/YELEK/GOZLUK eşlemesi |
| `src/tracker.py` | IoU tracker: aynı kişiyi takip eder, ihlal süresini biriktirir |
| `src/pipeline.py` | Ana döngü: oku → tespit et → eşik kontrol → bildir |
| `src/auth_client.py` | Backend’e login, JWT alır |
| `src/backend_client.py` | `POST /api/ihlaller` ve kamera heartbeat gönderir |
| `src/face_blur.py` | Kanıt fotoğrafında yüzleri bulanıklaştırır (KVKK yaklaşımı) |
| `cameras.json` / `cameras.*.json` | Çoklu kamera tanımları |
| `training/` | Model fine-tune rehberi ve araçlar |

### 5.5 YOLO ve sınıflar nasıl çalışır?

YOLO, bir karede “kutular” (bounding box) üretir: “burada bir nesne var, sınıfı X, güven skoru %Y”.

Projede kritik sınıflar:

- `Person` / `person` → insan
- `NO-Hardhat` → baret yok → sistemde **BARET**
- `NO-Safety Vest` → yelek yok → sistemde **YELEK**

`ppe_detector.py` içindeki sözlük bu dönüşümü yapar:

```text
NO-Hardhat      → BARET
NO-Safety Vest  → YELEK
NO-Goggles      → GOZLUK   (modelde yoksa çalışmaz)
```

Ayrıca PPE kutusu, bir **kişi kutusuna** yakın / örtüşmeli olmalıdır.  
Böylece masadaki bir nesne yanlışlıkla “yelek ihlali” sanılmaz.

### 5.6 Neden hemen kayıt atmıyoruz? (süre eşiği + cooldown)

Gerçek hayatta model bazen 1–2 kare yanlış görebilir. Bu yüzden:

1. **IoU Tracker** aynı kişiyi kareler arasında takip eder.
2. İhlal belli bir **minimum süre** (ör. ~8 saniye) boyunca devam ederse kayıt oluşur.
3. Aynı tip ihlal için **cooldown** vardır; her karede spam kayıt gitmez.

Bu, “yanlış alarmı azaltma” mühendisliğidir.

### 5.7 Kanıt fotoğrafı nasıl üretilir?

İhlal eşiği aşılınca:

1. O anki kare kopyalanır
2. Kişiye kırmızı çerçeve çizilir (gerekirse kutu biraz genişletilir)
3. İstenirse yüz blur uygulanır
4. Görüntü JPEG → Base64 string yapılır
5. Backend’e JSON olarak gönderilir

Backend bu string’i decode edip `backend/uploads/ihlaller/` altına dosya olarak kaydeder.

### 5.8 Tek kamera vs çoklu kamera

**Tek kamera (`.env`):**

```env
VIDEO_SOURCE=0
BOLGE_ID=1
```

`0` = bilgisayar webkamerası.

**Çoklu kamera (`cameras.json`):**

Her kamera kendi `bolge_id`, `video_source`, `kamera_adi` ile ayrı thread’de çalışır.

Örnek demo eşlemeleri (geliştirme döneminde kullanılmış):

| Fiziksel kaynak | Sistemdeki bölge adı |
|---|---|
| PC webkamerası | Veri Merkezi |
| Telefon (IP Webcam) | 1. Sıcak Haddehane |
| Tablet (IP Webcam) | 1. Soğuk Haddehane |
| Test videoları | Yüksek Fırın A / B |

Telefon bağlamak için tipik yol:

1. Telefona IP Webcam yükle
2. PC ile aynı Wi‑Fi
3. `http://TELEFON_IP:8080/video` adresini JSON’a yaz
4. `python -m src.main --cameras cameras.phone.json`

### 5.9 AI Core’u nasıl çalıştırırız?

```powershell
cd ai-core
.\venv\Scripts\Activate.ps1
# .env dosyasını .env.example'dan kopyalayıp düzenle
python -m src.main --show
```

Faydalı bayraklar:

| Bayrak | Anlamı |
|---|---|
| `--show` | Canlı önizleme penceresi açar (zorunlu değil) |
| `--loop` | Video dosyasını bitince başa sarar (canlı simülasyonu) |
| `--dry-run` | Backend’e göndermez; sadece tespit dener |
| `--cameras dosya.json` | Çoklu kamera config’i |
| `--source video.mp4` | Tek seferlik kaynak override |

Servis hesabı (yalnızca geliştirme):

- Kullanıcı: `ai_core_servis`
- Şifre: `AiCore123!`
- Rol: `AI_CORE_SERVIS` → sadece ihlal **yazma** yetkisi (panel girişi için değil)

### 5.10 Model eğitimi / fine-tune (kısa)

İlk model, Roboflow **Construction Site Safety** veri setinden türetilmiş bir YOLOv8 Nano modelidir.

Sonradan Erdemir sahasına özgü görsellerle iyileştirmek için:

1. Yanlış / zor örnekleri topla (`finetune-havuz` veya test görselleri)
2. Roboflow’da **aynı İngilizce sınıf adlarıyla** etiketle (`NO-Hardhat` vb.)
3. YOLOv8 formatında indir
4. Mevcut ağırlıklarla fine-tune et
5. Yeni `.pt` dosyasını `models/ppe_yolov8n.pt` yerine koy

Detay: `ai-core/training/README.md`

---

## 6) Backend — Merkezi beyin ve API

Klasör: `backend/`  
Tasarımda: **MODÜL-2** (API), **MODÜL-3** (JWT güvenlik), **MODÜL-6** (audit / reddetme / fine-tune)

### 6.1 Backend ne yapar?

Backend “hakem + arşiv” gibidir:

- Kim giriş yapabilir?
- Kim hangi bölgeyi görebilir?
- İhlal kaydı nasıl saklanır?
- Fotoğraf diske nasıl yazılır?
- İstatistik / rapor / log nasıl üretilir?

Frontend ve AI Core, backend’e **HTTP API** ile konuşur.

### 6.2 Teknolojiler

| Teknoloji | Neden? |
|---|---|
| **Java 21** | Tip güvenli, kurumsal backend dili |
| **Spring Boot** | REST API, güvenlik, DI, hızlı proje iskeleti |
| **Spring Security + JWT** | Login sonrası token ile yetkilendirme |
| **Spring Data JPA** | Entity ↔ tablo eşlemesi |
| **Flyway** | Veritabanı şemasını versiyonlu yönetme |
| **PostgreSQL** | İlişkisel, güvenilir veri saklama |
| **BCrypt** | Şifreleri hash’leme |
| **Maven Wrapper (`mvnw`)** | Herkeste aynı Maven sürümü |

### 6.3 Backend klasör mantığı (Spring’in katmanları)

Tipik Java paketi: `com.isg.ihlal.backend`

| Katman | Örnek | Ne yapar? |
|---|---|---|
| `controller` | `IhlalController`, `AuthController` | URL’leri dinler, HTTP cevap döner |
| `service` | `IhlalService`, `AuthService` | İş kuralları |
| `repository` | `IhlalRepository` | DB sorguları |
| `entity` | `Ihlal`, `Kullanici` | Tablo karşılığı Java sınıfları |
| `dto` | `IhlalKayitRequestDTO` | API’ye giren/çıkan veri paketleri |
| `security` | `JwtService`, filter | Token üret/doğrula |
| `config` | `WebConfig`, `SecurityConfig` | CORS, güvenlik ayarları |

**Öğrenci diliyle:**

- Controller = resepsiyon
- Service = işi yapan memur
- Repository = arşiv memuru
- Entity = dosya kartı
- DTO = dışarıya verilen form

### 6.4 Roller (kim ne yapabilir?)

| Rol | Ne görür / ne yapar? |
|---|---|---|
| **ISG_YONETICI** | Tüm fabrika ihlalleri, reddetme, kullanıcı yönetimi, raporlar |
| **FORMEN** | Kendi bölgesi (veya bağlı bölgeler), çözüldü işaretleme |
| **GORUNTULEYICI** | Salt okunur izleme (üst yönetim / misafir) |
| **AI_CORE_SERVIS** | Sadece `POST /api/ihlaller` (ve heartbeat gibi servis işleri) |

Yetkisiz işlem denemesi backend’de engellenir (`@PreAuthorize` + 403).

### 6.5 Önemli API uçları (endpoint’ler)

Bunlar “kapı numaraları” gibidir:

| Endpoint | Method | Kim kullanır? | Ne işe yarar? |
|---|---|---|---|
| `/api/auth/login` | POST | Herkes (giriş) | JWT üretir |
| `/api/ihlaller` | POST | AI Core | Yeni ihlal kaydı |
| `/api/ihlaller` | GET | Panel kullanıcıları | Liste (role göre filtreli) |
| `/api/ihlaller/{id}` | GET | Panel | Detay |
| `/api/ihlaller/{id}/reddet` | POST | Yönetici | Hatalı tespit |
| `/api/ihlaller/{id}/coz` | POST | Formen/yönetici | Çözüldü |
| `/api/ihlaller/istatistik` | GET | Panel | Pasta grafik / trend verisi |
| `/api/bolgeler` | GET | Panel | Bölge listesi |
| `/api/kullanicilar` | POST/GET… | Yönetici | Kullanıcı yönetimi |
| Kamera / rapor / log uçları | GET/POST | Panel / AI Core | Heartbeat, PDF rapor, denetim günlüğü |

### 6.6 JWT nedir? (öğrenci açıklaması)

1. Kullanıcı adı + şifre ile login olur.
2. Backend “bu kişi admin, bölge X” bilgisini imzalı bir **token** içine koyar.
3. Frontend her istekte `Authorization: Bearer <token>` gönderir.
4. Backend token’ı doğrular; geçersizse kapıyı açmaz.

Token’ı çalmak tehlikelidir; bu yüzden HTTPS (üretimde) ve kısa ömür / doğru saklama önemlidir. Geliştirmede token tarayıcıda tutulur.

### 6.7 İhlal yaşam döngüsü (durumlar)

| Durum | Anlamı |
|---|---|
| `AKTIF` | Yeni / henüz kapanmamış ihlal |
| `COZULDU` | Formen/yönetici sahada ele aldı, kapattı |
| `HATALI_TESPIT` | Model yanlış alarm vermiş; istatistikten düşer |

Yanlış tespitler `islem_loglari` tablosuna da işlenir (denetim izi).  
Ayrıca orijinal foto `uploads/finetune-havuz/{tip}/` altına kopyalanabilir → ileride modeli eğitmek için veri olur.

### 6.8 Flyway migration’lar neden önemli?

Elle “şu SQL’i çalıştır” demek kırılgandır. Flyway ile:

- Şema değişiklikleri dosya olarak versiyonlanır (`V1`, `V2`, … `V16`…)
- Backend açılınca eksik migration otomatik uygulanır
- Ekip aynı veritabanı yapısında çalışır

Örnek ilerleme:

- V1–V2: temel şema + seed
- V4–V5: AI Core servis hesabı / rolü
- V6: blur kolonunun kaldırılması (tasarım değişikliği)
- V8: personel + çözüldü
- V9+: soğuk haddehane, MVP paket, yüksek fırın A/B vb.

### 6.9 Backend’i çalıştırma

```powershell
# 1) Önce veritabanı
docker compose up -d

# 2) Backend
cd backend
.\mvnw.cmd spring-boot:run
```

API adresi: `http://localhost:8080`

---

## 7) Frontend — Kullanıcının gördüğü yüz

Klasör: `frontend/`  
Tasarımda: **MODÜL-4** (yönetici paneli), **MODÜL-5** (formen paneli) + ortak bileşenler

### 7.1 Frontend ne yapar?

Frontend, tarayıcıda çalışan arayüzdür:

- Giriş ekranı
- Yönetici / formen / izleyici panelleri
- İhlal listesi, detay fotoğrafı, grafikler
- Reddet / çözüldü / dışa aktarma gibi butonlar
- Kamera durumu, profil, kullanıcı yönetimi (geliştirilmiş sürümde)

**İş kuralını tek başına uygulamaz.** Yetkiyi backend de doğrular. Frontend sadece kullanıcı deneyimini sunar ve API’yi çağırır.

### 7.2 Teknolojiler

| Teknoloji | Ne işe yarar? |
|---|---|
| **Angular (standalone)** | Sayfa / bileşen / routing iskeleti |
| **TypeScript** | Tip güvenli JavaScript |
| **HttpClient** | Backend’e istek |
| **Functional interceptors** | Her isteğe JWT ekleme |
| **Route guards** | Yetkisiz sayfaya girmeyi engelleme |
| **Chart.js + ng2-charts** | Pasta / istatistik grafikleri |
| **Signals** | Modern Angular durum yönetimi yaklaşımı |

### 7.3 Klasör yapısı (öğrenci haritası)

```text
frontend/src/app/
  core/                 → uygulamanın omurgası
    models/             → TypeScript arayüzleri (DTO karşılıkları)
    services/           → AuthService, IhlalService, ...
    interceptors/       → jwtInterceptor
    guards/             → auth / admin / foreman / viewer
    directives/         → AuthImgDirective (korumalı foto)
  features/             → sayfalar
    anasayfa/
    login/
    admin-dashboard/
    foreman-dashboard/
    viewer-dashboard/
    iletisim/
    uyelik-basvurusu/
    ...
  shared/               → ortak parçalar
    components/         → ihlal listesi, grafik, modal, kamera paneli...
    layout/             → header, footer, panel kabuğu
```

### 7.4 Sayfa / rota mantığı

`app.routes.ts` kabaca şöyle çalışır:

| Yol | Sayfa | Kim girebilir? |
|---|---|---|
| `/` | Anasayfa (tanıtım) | Herkes |
| `/giris` | Login | Herkes |
| `/yonetici` | Admin dashboard | `ISG_YONETICI` |
| `/formen` | Formen dashboard | `FORMEN` |
| `/izleyici` | Salt okunur panel | `GORUNTULEYICI` |

Guard’lar şunu sorar: “Token var mı? Rol doğru mu?”  
Cevap hayırsa kullanıcıyı girişe veya ana sayfaya yollar.

### 7.5 Ortak bileşenler

| Bileşen | Ne yapar? |
|---|---|
| `IhlalListesiComponent` | Tablo: tarih, bölge, tip, durum |
| `IstatistikGrafikComponent` | Pasta grafik / trend |
| `IhlalDetayModalComponent` | Büyük foto + aksiyon butonları |
| `KameraDurumPaneli` | AI Core heartbeat’lerinden online/offline |
| `DenetimGunlugu` | Kim ne yaptı logları |
| `ProfilPaneli` / kullanıcı yönetimi | Hesap işlemleri |

### 7.6 JWT interceptor + AuthImg neden var?

1. **Interceptor:** Her API isteğine otomatik `Authorization` header ekler.  
   Yoksa her serviste tek tek token yazmak gerekir ve unutulur.

2. **AuthImgDirective:** `<img src="...">` normalde Authorization gönderemez.  
   Bu yüzden fotoğraflar JWT’li HTTP isteğiyle çekilip blob URL olarak gösterilir.  
   Aksi halde “foto 401 Unauthorized” hatası alınır.

### 7.7 Frontend’i çalıştırma

```powershell
cd frontend
npm install
ng serve
```

Adres: `http://localhost:4200`  
Geliştirme API adresi genelde: `http://localhost:8080/api`

### 7.8 Test kullanıcıları (yalnızca geliştirme)

| Kullanıcı | Şifre | Rol |
|---|---|---|
| `admin` | `Admin123!` | İSG yöneticisi |
| `formen1` | `Formen123!` | Formen |
| `izleyici` | `Izleyici123!` | Görüntüleyici |

> Bunlar demo/test içindir. Gerçek üretimde mutlaka değiştirilir.

---

## 8) Veritabanı — Kalıcı hafıza

Veritabanı PostgreSQL’dir. Docker ile çalışır.

### 8.1 Ana tablolar (sade anlatım)

| Tablo | Ne tutar? |
|---|---|
| `bolgeler` | Fabrika bölgeleri (Yüksek Fırın A, Sıcak Haddehane…) |
| `ihlal_tipleri` | BARET / YELEK / GOZLUK |
| `kullanicilar` | Login olan insanlar + roller |
| `ihlaller` | Sistemin ana işlem defteri (kanıt yolu, zaman, durum) |
| `islem_loglari` | Giriş, reddetme vb. denetim kayıtları |
| `personel` | (sonraki faz) personel özetleri için |
| `kamera_durumlari` | AI Core’un “ben çalışıyorum” kalp atışları |

### 8.2 İlişkiler neden önemli?

Örnek:

- Her ihlalin bir `bolge_id`’si vardır → “nerede oldu?”
- Her ihlalin bir `ihlal_tipi_id`’si vardır → “ne tür ihlal?”
- Formen kullanıcısının `bolge_id`’si vardır → “sadece kendi bölgesini gör”

Bu foreign key yapısı sayesinde “formen yanlışlıkla başka bölgeyi görsün” gibi hatalar SQL/API katmanında engellenir.

### 8.3 pgAdmin

`http://localhost:5050` üzerinden tabloları görsel olarak inceleyebilirsin.  
Geliştirmede SQL öğrenmek / seed veriyi kontrol etmek için çok faydalıdır.

---

## 9) Güvenlik ve KVKK yaklaşımı

### 9.1 Rol bazlı erişim

- Formen: kendi sahası
- Yönetici: tüm fabrika
- Görüntüleyici: sadece bakma
- AI Core hesabı: panel değil, sadece veri yazma

### 9.2 Kanıt fotoğrafları

Başlangıç tasarımında **orijinal + yüzü blurlu** iki kopya vardı (KVKK).  
Sonraki bir geliştirmede blur zorunluluğu kaldırılıp sadeleştirildi; AI Core tarafında yüz blur kodu yine mevcut olabilir ve kanıt karesinde kullanılabilir. Önemli fikir şudur:

> Amaç “kişi avı” değil, **risk takibi ve İSG farkındalığıdır**.

### 9.3 Şifreler

Veritabanında düz şifre tutulmaz. BCrypt hash tutulur.

---

## 10) Proje klasörleri tek bakışta

```text
isg_ihlal_projesi_demo/
├── ai-core/                 # Yapay zekâ servisi (Python)
│   ├── src/                 # Ana kod
│   ├── models/              # YOLO ağırlıkları (.pt)
│   ├── training/            # Fine-tune rehberi
│   ├── test_videos/         # Kamera yokken deneme videoları
│   └── cameras*.json        # Kamera konfigürasyonları
├── backend/                 # Spring Boot API
│   ├── src/main/java/...    # Java kaynak kodu
│   ├── src/main/resources/
│   │   ├── application.yml
│   │   └── db/migration/    # Flyway SQL'leri
│   └── uploads/             # Kanıt fotoğrafları + fine-tune havuzu
├── frontend/                # Angular web paneli
│   └── src/app/             # Ekranlar ve servisler
├── scripts/                 # Otomasyon (smoke test, flyway, start script)
├── docker-compose.yml       # Postgres + pgAdmin
├── tasarim_mimari.md        # Resmi tasarım
├── ILERLEME_GUNLUGU*.md     # Ne zaman ne yapıldı
└── README.md                # Hızlı çalıştırma
```

---

## 11) Sistemi baştan sona ayağa kaldırma (pratik sıra)

Üç (aslında dört) süreç ayrı terminallerde çalışır:

### Adım 1 — Veritabanı

```powershell
docker compose up -d
```

- Postgres: `localhost:5432`
- pgAdmin: `http://localhost:5050`

### Adım 2 — Backend

```powershell
cd backend
.\mvnw.cmd spring-boot:run
```

### Adım 3 — Frontend

```powershell
cd frontend
npm install
ng serve
```

Panel: `http://localhost:4200`

### Adım 4 — AI Core

```powershell
cd ai-core
.\venv\Scripts\Activate.ps1
python -m src.main --show
```

veya çoklu kamera / yüksek fırın script’leri (`scripts/start-yuksek-firin.ps1` vb.).

**Sıra önemli:** Önce DB, sonra backend, sonra AI Core / frontend.  
AI Core, backend ayakta değilse ihlal kaydı atamaz.

---

## 12) Sık karşılaşılan kavramlar sözlüğü

| Kavram | Anlamı |
|---|---|
| **KKD / KDD** | Kişisel Koruyucu Donanım (baret, yelek, gözlük…) |
| **İSG** | İş Sağlığı ve Güvenliği |
| **RTSP** | IP kameraların video akışı protokolü |
| **Frame / kare** | Videodaki tek bir görüntü anı |
| **YOLO** | Gerçek zamanlı nesne tespit modeli ailesi |
| **Bounding box** | Nesnenin etrafındaki dikdörtgen kutu |
| **Confidence** | Modelin “ne kadar emin olduğu” skoru |
| **False positive** | Aslında ihlal yokken “ihlal var” demek |
| **IoU** | İki kutunun örtüşme oranı; takip için kullanılır |
| **Cooldown** | Aynı olayın peş peşe tekrar kaydını engelleyen bekleme |
| **JWT** | Giriş sonrası imzalı kimlik bileti |
| **DTO** | API’de taşınan veri paketi |
| **Entity** | Veritabanı tablosunun Java karşılığı |
| **Flyway** | SQL şema versiyonlama aracı |
| **Guard** | Angular’da sayfa koruması |
| **Interceptor** | Her HTTP isteğine otomatik ek işlem |
| **Fine-tune** | Mevcut modeli yeni verilerle biraz daha eğitmek |
| **Heartbeat** | “Kamera/servis hâlâ canlı” sinyali |
| **Seed data** | Sistem ilk açılışta yüklenen örnek veri |

---

## 13) Bilinen sınırlamalar (dürüstçe)

1. **GOZLUK** sınıfı mevcut PPE modelinde yok; BARET ve YELEK çalışır.
2. Kişi ↔ ekipman eşlemesi merkez mesafesi / IoU ile yapılır; mükemmel insan kimliği tanıma değildir.
3. Cooldown kişi kimliğinden çok ihlal tipi / takip mantığına bağlıdır.
4. Büyük model dosyaları ve bazı test videoları git’te olmayabilir; yerelde ayrıca konur.
5. Port çakışmaları (5432 Postgres, 8080 backend) geliştirmede sık görülür; eski süreç kapatılmalıdır.
6. Telefon IP’si Wi‑Fi değişince `cameras.*.json` güncellenmelidir.

Bunlar “proje başarısız” demek değildir; **gerçekçi mühendislik sınırlarıdır**.

---

## 14) Bu projeden öğrenilenler (öğrenci gözüyle)

Bu proje tek bir ders konusu değil; birçok alanı birleştirir:

1. **Yazılım mimarisi:** Katmanlara ayırma (AI / API / UI)
2. **Veritabanı tasarımı:** Tablolar, FK, constraint, migration
3. **Güvenlik:** Hash’li şifre, JWT, rol bazlı yetki
4. **Bilgisayarlı görü:** YOLO, OpenCV, tracker, false-positive azaltma
5. **Frontend mühendisliği:** Guard, interceptor, component paylaşımı
6. **DevOps benzeri pratik:** Docker, script’ler, branch stratejisi
7. **İSG domain bilgisi:** KKD, saha rolleri (formen / İSG yöneticisi), kanıtlı kayıt
8. **Geri bildirim döngüsü:** Yanlış tespit → reddet → fine-tune havuzu → daha iyi model

---

## 15) “Sınavda / sunumda anlat” diye kısa senaryo

İstersen şöyle anlatabilirsin:

> “Mevcut güvenlik kameralarını kullanarak baret ve yelek ihlallerini otomatik yakalayan üç katmanlı bir sistem geliştirdik.  
> Python tarafındaki AI Core, YOLOv8 ile görüntüyü analiz ediyor; ihlal süreyi aşıınca kanıt fotoğrafını Spring Boot backend’e gönderiyor.  
> Backend kaydı PostgreSQL’e yazıyor ve JWT ile rol bazlı erişim sunuyor.  
> Angular panelde İSG yöneticisi tüm fabrikayı, formen kendi bölgesini takip ediyor; yanlış alarmlar reddedilip model iyileştirme havuzuna düşüyor.  
> Böylece amaç, kaza olduktan sonra değil, kaza olmadan önce müdahale etmek.”

---

## 16) Son söz

Bu proje “sadece bir YOLO demosu” değildir.  
**Tespit + kayıt + yetki + arayüz + geri bildirim** zincirini uçtan uca kurar.

- AI Core olmadan: kimse otomatik bakmaz  
- Backend olmadan: veri kalıcı ve güvenli olmaz  
- Frontend olmadan: saha personeli sistemi kullanamaz  

Üçü birlikte çalışınca ortaya çıkan şey:  
**kamera görüntüsünden İSG ihlali yakalayan, kaydeden ve yönetilebilir hale getiren bir yazılım sistemi.**

Daha kısa çalıştırma için [`README.md`](./README.md),  
tasarımın “anayasası” için [`tasarim_mimari.md`](./tasarim_mimari.md) dosyalarına bakabilirsin.
