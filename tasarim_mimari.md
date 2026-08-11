# İSG KURAL İHLAL TESPİT VE UYARI SİSTEMİ – TASARIM SÜRECİ DOKÜMANI

**SORUMLU**  
Beyza Erdem

**Doküman sürümü:** 2.0 (revize — güncel uygulama)  
**Önceki sürüm:** 1.0 (ilk tasarım PDF’i)  
**Tarih:** 10 Ağustos 2026

---

## GENEL AÇIKLAMALAR

### GENEL TANIMLAR

- Amaç, Erdemir üretim sahalarında baret veya yelek (KDD) takmayan personelin gerçek zamanlı olarak tespit edilerek olası iş kazalarının kaza yaşanmadan önlenmesidir. Gözlük (GOZLUK) tipi veritabanında tanımlıdır; mevcut PPE modelinde sınıf olmadığı için canlı tespit üretilmez (ileride fine-tune ile açılır).
- Sistem üç ana katmandan oluşur: (1) canlı kamera görüntüsünü işleyen ve KDD ihlallerini tespit eden Python/OpenCV/YOLOv8 tabanlı Yapay Zeka Görüntü İşleme servisi (AI Core), (2) verileri kalıcı hale getiren ve yetki bazlı erişim sunan Java Spring Boot tabanlı RESTful API (Backend), (3) kullanıcıların bulgularla etkileşime girdiği Angular tabanlı web arayüzü (Frontend).
- Temel amaç, üretim sahasındaki KDD ihlallerini insan müdahalesi olmadan, gerçek zamanlı ve mevcut kamera altyapısına sıfır donanım maliyetiyle tespit ederek olası bir iş kazasını proaktif olarak önlemektir.
- Her ihlal tek kanıt fotoğrafı ile kaydedilir. Erişim ayrımı rol ve bölge yetkisiyle yapılır: FORMEN yalnızca bağlı olduğu bölge(ler)in kayıtlarını, ISG_YONETICI tüm fabrikayı, GORUNTULEYICI salt okunur tüm fabrikayı görür. (İlk tasarımda orijinal+blurlu çift foto ve role göre blur ayrımı vardı; kaldırılmıştır — bkz. REVİZYON NOTLARI.)
- Bu doküman, geliştirme ekibinin tek referans kaynağı olacak şekilde; veritabanı tabloları ve kısıtları (constraints), API request/response modelleri (DTO), backend endpoint listesi, frontend bileşen hiyerarşisi ve her modülün somut aksiyon listesini bir arada sunar.

### DİĞER AÇIKLAMALAR

- Kimlik doğrulama ve yetkilendirme JWT (JSON Web Token) ile yapılır. Sistemde dört rol tanımlıdır: ISG_YONETICI (tüm fabrika), FORMEN (bağlı bölge/bölgeler), GORUNTULEYICI (salt okunur), AI_CORE_SERVIS (yalnızca ihlal yazma ve kamera heartbeat). Yetkisiz erişim denemeleri backend tarafında 403 Forbidden ile engellenir.
- Veritabanı olarak PostgreSQL kullanılır; şema Flyway migration’ları (V1–V17) ile versiyonlanır. Bölge, kullanıcı, personel, ihlal tipi ve ihlal kayıtları foreign key ilişkileriyle bağlıdır.
- Görüntü işleme tarafı Python, OpenCV ve YOLOv8 Nano (Construction Site Safety fine-tune: `ppe_yolov8n.pt`) ile gerçekleştirilir. IoU tracker ile ihlal süresi biriktirilir; eşik aşılınca kanıt karesi üretilir. Opsiyonel kişi tanıma YuNet + SFace ile yapılır.
- Test ve entegrasyon aşamasında gerçek kamera akışı yerine test videoları, webkamera, telefon/tablet IP Webcam ve önceden yapılandırılmış seed veritabanı kayıtları kullanılır; canlı kamera altyapısı olmadan da uçtan uca test yapılabilir.
- Sistem, kamera/bölge sayısı arttıkça yatay olarak ölçeklenebilecek şekilde tasarlanır; Python tarafı kamera başına thread/worker olarak çoğaltılabilir, Backend ve veritabanı katmanı bu artışı bölge bazlı foreign key ve `kullanici_bolgeler` yapısıyla karşılar.
- Sıfır donanım maliyeti hedefi gereği sistem yalnızca yazılım katmanında konumlanır; mevcut IP kameralardan görüntü akışı RTSP/HTTP protokolleri üzerinden okunur.
- Yapay zekanın üretebileceği yanlış pozitif tespitler için denetim/geri bildirim mekanizması (MODÜL-6) tasarlanmıştır; reddedilen kayıtlar istatistiklerden düşer ve fine-tune havuzuna kopyalanır.

---

## REVİZYON NOTLARI (v1 → v2)

### SİLİNEN / KALDIRILAN

| Madde | Açıklama |
|---|---|
| `blurlu_foto_yolu` kolonu | ihlaller tablosundan düşürüldü (Flyway V6) |
| `blurluFotoBase64` DTO alanı | IhlalKayitRequestDTO’dan kaldırıldı |
| Çift fotoğraf politikası | Orijinal + blurlu zorunluluğu kaldırıldı; tek kanıt fotoğrafı tutulur |
| Role göre blurlu/orijinal ayrımı | Formen blurlu / yönetici orijinal kuralı kaldırıldı |
| Grafikte “Telefon” ihlal tipi | Kapsam dışı; seed’de yalnızca BARET / YELEK / GOZLUK |

### EKLENEN

| Madde | Açıklama |
|---|---|
| Roller: GORUNTULEYICI, AI_CORE_SERVIS | Salt okunur panel; AI Core servis hesabı |
| Durum: COZULDU | Saha müdahalesi kapatma (`POST .../coz`) |
| TABLO personeller | Sicil, ad soyad, departman |
| TABLO personel_yuzleri | Kişi tanıma referans yüzleri |
| TABLO kamera_durumlari | AI Core heartbeat |
| TABLO kullanici_bolgeler | Formen çoklu bölge |
| ihlaller alanları | personel_id, cozen_kullanici_id, cozme_zamani, coz_notu, sure_saniye |
| kullanicilar alanları | eposta, telefon, gorev |
| islem_loglari alanları | denenen_kullanici_adi (başarısız giriş); kullanici_id NULL olabilir |
| COMPONENT ViewerDashboard | `/izleyici` |
| COMPONENT KameraDurumPaneli, ProfilPaneli, DenetimGunlugu, KullaniciYonetim, Personel/Kalite panelleri | Panel genişletmeleri |
| MODÜL-7 Kamera sağlık, MODÜL-8 Personel/yüz tanıma, MODÜL-9 Raporlama | Yeni modüller |
| Endpoint’ler | coz, heartbeat, personel, rapor, islem-loglari, profil, istatistik/kalite, istatistik/personel, finetune senkron |
| AI Core | IoU tracker, süre eşiği, cooldown, çoklu kamera, yüz tanıma |
| Fine-tune havuzu | `uploads/finetune-havuz/{tip}/` |

### YAPILMAYAN / KISMİ

| Madde | Açıklama |
|---|---|
| GOZLUK canlı tespiti | Tip DB’de var; modelde NO-Goggles yok |
| Gerçek fabrika RTSP üretimi | Mimari hazır; demo kaynaklar kullanılıyor |
| Nesne depolama (S3) | Yerel `backend/uploads/` |
| Kurumsal IdP / üretim TLS | Dev ortamı HTTP + BCrypt |

---

## VERİ TABANI

### TABLO-1 : bolgeler

**Tablo Tanımı:** Fabrika içindeki üretim bölgelerini (vardiya/departman) tanımlayan referans tablodur. Formen yetkilendirmesi ve ihlal kayıtlarının konumlandırılması bu tabloya bağlı bolge_id üzerinden yapılır.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Bölge birincil anahtarı |
| bolge_adi | VARCHAR(100) | NOT NULL | - | Bölge/vardiya adı (ör. Yüksek Fırın A Bolgesi) |
| aciklama | VARCHAR(255) | NULL | - | Bölgeye ait ek açıklama |

### TABLO-2 : ihlal_tipleri

**Tablo Tanımı:** Tespit edilebilecek KDD (Kişisel Koruyucu Donanım) ihlal tiplerini tanımlayan referans/lookup tablodur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | SMALLINT | NOT NULL | PK | İhlal tipi birincil anahtarı |
| tip_adi | VARCHAR(50) | NOT NULL | - | BARET / YELEK / GOZLUK |
| aciklama | VARCHAR(255) | NULL | - | İhlal tipine ait ek açıklama |

### TABLO-3 : kullanicilar

**Tablo Tanımı:** Sisteme giriş yapacak İSG yöneticisi, formen, görüntüleyici ve AI Core servis hesabı personelini tutan tablodur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Kullanıcı birincil anahtarı |
| kullanici_adi | VARCHAR(50) | NOT NULL | UNIQUE | Benzersiz giriş adı |
| sifre_hash | VARCHAR(255) | NOT NULL | - | BCrypt ile şifrelenmiş parola |
| ad_soyad | VARCHAR(100) | NOT NULL | - | Kullanıcının adı soyadı |
| rol | VARCHAR(20) | NOT NULL | - | ISG_YONETICI / FORMEN / GORUNTULEYICI / AI_CORE_SERVIS |
| bolge_id | BIGINT | NULL | FK | bolgeler.id — birincil bölge (FORMEN; geriye dönük) |
| aktif_mi | BOOLEAN | NOT NULL | - | Kullanıcının aktif/pasif durumu (varsayılan: true) |
| eposta | VARCHAR(120) | NULL | - | Profil e-posta (EKLENEN) |
| telefon | VARCHAR(30) | NULL | - | Profil telefon (EKLENEN) |
| gorev | VARCHAR(150) | NULL | - | Unvan / görev (EKLENEN) |

### TABLO-3b : kullanici_bolgeler (EKLENEN)

**Tablo Tanımı:** Formen’in birden fazla bölgeye bağlanmasını sağlayan N:N ilişki tablosudur (ör. Yüksek Fırın A + B).

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| kullanici_id | BIGINT | NOT NULL | PK, FK | kullanicilar.id |
| bolge_id | BIGINT | NOT NULL | PK, FK | bolgeler.id |

### TABLO-4 : ihlaller

**Tablo Tanımı:** Python AI Core servisi tarafından tespit edilen her bir KDD ihlalinin kanıt fotoğrafı, konumu, zamanı, personel eşlemesi ve inceleme durumu ile kaydedildiği sistemin ana işlem (transactional) tablosudur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | İhlal kaydı birincil anahtarı |
| bolge_id | BIGINT | NOT NULL | FK | bolgeler.id — ihlalin tespit edildiği bölge |
| ihlal_tipi_id | SMALLINT | NOT NULL | FK | ihlal_tipleri.id — tespit edilen ihlalin tipi |
| tespit_zamani | TIMESTAMP | NOT NULL | - | AI Core’un ihlali tespit ettiği an |
| orijinal_foto_yolu | VARCHAR(500) | NOT NULL | - | Kanıt fotoğrafının depolama yolu/URL’i |
| durum | VARCHAR(20) | NOT NULL | - | AKTIF / HATALI_TESPIT / COZULDU (varsayılan: AKTIF) |
| personel_id | BIGINT | NULL | FK | personeller.id — eşleşen saha personeli (EKLENEN) |
| reddeden_kullanici_id | BIGINT | NULL | FK | kullanicilar.id — hatalı tespit işaretleyen yönetici |
| red_zamani | TIMESTAMP | NULL | - | Kaydın hatalı tespit olarak işaretlendiği an |
| cozen_kullanici_id | BIGINT | NULL | FK | kullanicilar.id — çözen kullanıcı (EKLENEN) |
| cozme_zamani | TIMESTAMP | NULL | - | Çözüm zamanı (EKLENEN) |
| coz_notu | VARCHAR(500) | NULL | - | Opsiyonel çözüm notu (EKLENEN) |
| sure_saniye | INT | NULL | - | Tracker birikimli ihlal süresi (EKLENEN) |
| olusturma_zamani | TIMESTAMP | NOT NULL | - | Kaydın veritabanına yazıldığı an (varsayılan: now()) |

> **SİLİNEN (v1):** `blurlu_foto_yolu VARCHAR(500) NOT NULL`

### TABLO-5 : islem_loglari

**Tablo Tanımı:** Kullanıcıların sistem üzerinde gerçekleştirdiği kritik işlemleri (giriş, ihlal reddetme, çözme, başarısız giriş vb.) izlenebilirlik ve denetim amacıyla kaydeden log tablosudur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Log kaydı birincil anahtarı |
| kullanici_id | BIGINT | NULL | FK | kullanicilar.id — işlemi yapan (başarısız girişte NULL olabilir) |
| denenen_kullanici_adi | VARCHAR(50) | NULL | - | Başarısız giriş denenen ad (EKLENEN) |
| islem_tipi | VARCHAR(50) | NOT NULL | - | GIRIS / IHLAL_REDDETME / IHLAL_COZME / BASARISIZ_GIRIS vb. |
| ilgili_ihlal_id | BIGINT | NULL | FK | ihlaller.id — işlemin ilişkili olduğu ihlal kaydı (varsa) |
| islem_zamani | TIMESTAMP | NOT NULL | - | İşlemin gerçekleştiği an |
| detay | VARCHAR(255) | NULL | - | İşleme dair serbest metin açıklama |

### TABLO-6 : personeller (EKLENEN)

**Tablo Tanımı:** Kamerada tespit edilen / sicil ile eşleşen saha personelini tutan referans tablodur. `kullanicilar` (login) tablosundan bağımsızdır.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Personel birincil anahtarı |
| sicil_no | VARCHAR(50) | NOT NULL | UNIQUE | Sicil numarası |
| ad_soyad | VARCHAR(100) | NOT NULL | - | Ad soyad |
| departman | VARCHAR(100) | NULL | - | Departman |
| bolge_id | BIGINT | NULL | FK | bolgeler.id |
| aktif_mi | BOOLEAN | NOT NULL | - | Varsayılan: true |

### TABLO-7 : personel_yuzleri (EKLENEN)

**Tablo Tanımı:** Kişi tanıma için her personele ait referans yüz fotoğraflarını tutar. AI Core galeriyi yükleyip embedding üretir.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Yüz kaydı birincil anahtarı |
| personel_id | BIGINT | NOT NULL | FK | personeller.id (ON DELETE CASCADE) |
| foto_yolu | VARCHAR(500) | NOT NULL | - | Referans fotoğraf yolu |
| olusturma_zamani | TIMESTAMP | NOT NULL | - | Kayıt zamanı |

### TABLO-8 : kamera_durumlari (EKLENEN)

**Tablo Tanımı:** AI Core’un periyodik heartbeat mesajlarıyla güncellediği kamera çevrimiçi/çevrimdışı durum tablosudur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Kayıt birincil anahtarı |
| bolge_id | BIGINT | NOT NULL | FK | bolgeler.id |
| kamera_adi | VARCHAR(100) | NOT NULL | - | Kamera adı (bolge_id + ad UNIQUE) |
| online_mi | BOOLEAN | NOT NULL | - | Çevrimiçi mi |
| son_kare_zamani | TIMESTAMP | NULL | - | Son işlenen kare zamanı |
| fps | DOUBLE | NULL | - | FPS tahmini |
| guncelleme_zamani | TIMESTAMP | NOT NULL | - | Son heartbeat zamanı |

### DB CONSTRAINTS

| Kısıt Adı | Kısıt Tipi | Tablo | Tanım |
|---|---|---|---|
| fk_ihlal_bolge | FOREIGN KEY | ihlaller | ihlaller.bolge_id → bolgeler.id (ON DELETE RESTRICT) |
| fk_ihlal_tip | FOREIGN KEY | ihlaller | ihlaller.ihlal_tipi_id → ihlal_tipleri.id |
| fk_ihlal_red_kullanici | FOREIGN KEY | ihlaller | ihlaller.reddeden_kullanici_id → kullanicilar.id (NULL olabilir) |
| fk_ihlal_cozen_kullanici | FOREIGN KEY | ihlaller | ihlaller.cozen_kullanici_id → kullanicilar.id (EKLENEN) |
| fk_ihlal_personel | FOREIGN KEY | ihlaller | ihlaller.personel_id → personeller.id (EKLENEN) |
| fk_kullanici_bolge | FOREIGN KEY | kullanicilar | kullanicilar.bolge_id → bolgeler.id |
| pk_kullanici_bolgeler | PRIMARY KEY | kullanici_bolgeler | (kullanici_id, bolge_id) (EKLENEN) |
| uq_kullanici_adi | UNIQUE | kullanicilar | kullanici_adi alanı benzersiz olmalıdır |
| uq_personel_sicil | UNIQUE | personeller | sicil_no benzersiz (EKLENEN) |
| uq_kamera_bolge_adi | UNIQUE | kamera_durumlari | (bolge_id, kamera_adi) (EKLENEN) |
| ck_kullanici_rol | CHECK | kullanicilar | rol IN ('ISG_YONETICI','FORMEN','GORUNTULEYICI','AI_CORE_SERVIS') |
| ck_ihlal_durum | CHECK | ihlaller | durum IN ('AKTIF','HATALI_TESPIT','COZULDU') |
| fk_log_kullanici | FOREIGN KEY | islem_loglari | islem_loglari.kullanici_id → kullanicilar.id |
| fk_log_ihlal | FOREIGN KEY | islem_loglari | islem_loglari.ilgili_ihlal_id → ihlaller.id (NULL olabilir) |
| fk_personel_yuz_personel | FOREIGN KEY | personel_yuzleri | personel_id → personeller.id ON DELETE CASCADE (EKLENEN) |
| fk_kamera_bolge | FOREIGN KEY | kamera_durumlari | kamera_durumlari.bolge_id → bolgeler.id (EKLENEN) |

---

## VERİ MODELLERİ

### DTO-1 : IhlalKayitRequestDTO

**Model Tanımı:** Python AI Core servisinin tespit ettiği bir ihlali Java Backend API’sine iletmek için POST isteğinde kullandığı model.

| Alan | Tip | Açıklama |
|---|---|---|
| bolgeId | Long | İhlalin tespit edildiği bölgenin kimliği |
| ihlalTipiId | Short | Tespit edilen ihlal tipinin kimliği (baret/yelek/gözlük) |
| tespitZamani | LocalDateTime | İhlalin tespit edildiği an (ISO-8601) |
| orijinalFotoBase64 | String | Kanıt fotoğrafının base64 kodlu içeriği |
| personelId | Long | Opsiyonel personel eşlemesi (EKLENEN) |
| personelSicilNo | String | Opsiyonel sicil ile eşleme (EKLENEN) |
| sureSaniye | Integer | Opsiyonel tracker süresi saniye (EKLENEN) |

> **SİLİNEN (v1):** `blurluFotoBase64 String`

### DTO-2 : IhlalResponseDTO

**Model Tanımı:** Frontend’e ihlal listesi/detayı döndürülürken kullanılan model.

| Alan | Tip | Açıklama |
|---|---|---|
| id | Long | İhlal kaydının kimliği |
| bolgeAdi | String | İhlalin tespit edildiği bölgenin adı |
| ihlalTipiAdi | String | Tespit edilen ihlal tipinin adı |
| tespitZamani | LocalDateTime | İhlalin tespit edildiği an |
| fotoUrl | String | Kanıt fotoğrafının erişim adresi |
| durum | String | AKTIF / HATALI_TESPIT / COZULDU |
| personelId | Long | Eşleşen personel id (EKLENEN) |
| personelAdi | String | Personel adı (EKLENEN) |
| personelSicilNo | String | Sicil no (EKLENEN) |
| cozNotu | String | Çözüm notu (EKLENEN) |
| sureSaniye | Integer | İhlal süresi (EKLENEN) |

### DTO-3 : LoginRequestDTO

**Model Tanımı:** Kullanıcının sisteme giriş isteğinde gönderdiği kimlik bilgilerini taşıyan model.

| Alan | Tip | Açıklama |
|---|---|---|
| kullaniciAdi | String | Kullanıcının giriş adı |
| sifre | String | Kullanıcının parolası (düz metin, TLS üzerinden iletilir) |

### DTO-4 : LoginResponseDTO

**Model Tanımı:** Başarılı girişte backend tarafından üretilen JWT ve kullanıcı bağlam bilgilerini taşıyan model.

| Alan | Tip | Açıklama |
|---|---|---|
| token | String | Kullanıcının rol/bölge bilgisini içeren imzalı JWT |
| kullaniciId | Long | Kullanıcı kimliği (EKLENEN) |
| kullaniciAdi | String | Giriş adı (EKLENEN) |
| rol | String | ISG_YONETICI / FORMEN / GORUNTULEYICI / AI_CORE_SERVIS |
| adSoyad | String | Kullanıcının adı soyadı |
| bolgeId | Long | Birincil bölge kimliği (FORMEN için dolu) |
| bolgeIds | List | Tüm yetkili bölgeler (FORMEN; EKLENEN) |

### DTO-5 : IhlalIstatistikDTO

**Model Tanımı:** Dashboard’lardaki pasta grafik ve trend özetlerinde kullanılan, bölge/tip bazlı toplu istatistik modeli.

| Alan | Tip | Açıklama |
|---|---|---|
| bolgeAdi | String | İstatistiğin ait olduğu bölge |
| ihlalTipiAdi | String | İstatistiğin ait olduğu ihlal tipi |
| toplamAdet | Integer | Seçilen periyottaki toplam ihlal adedi (HATALI_TESPIT hariç) |
| yuzdeDegisim | Double | Önceki haftaya göre yüzdesel değişim (ör. +20.0) |

### DTO-6 : IhlalRedRequestDTO

**Model Tanımı:** İSG yöneticisinin yanlış pozitif bir tespiti reddederken gönderdiği model.

| Alan | Tip | Açıklama |
|---|---|---|
| ihlalId | Long | Hatalı olduğu düşünülen ihlal kaydının kimliği |
| redNedeni | String | Reddetme gerekçesine dair opsiyonel açıklama |

### DTO-7 : IhlalCozRequestDTO (EKLENEN)

**Model Tanımı:** Formen/yöneticinin ihlali “Çözüldü” olarak kapatırken gönderdiği model.

| Alan | Tip | Açıklama |
|---|---|---|
| not | String | Opsiyonel çözüm notu (max 500) |

### DTO-8 : KameraHeartbeatDTO (EKLENEN)

**Model Tanımı:** AI Core’un kamera sağlık bildirimini taşıyan model.

| Alan | Tip | Açıklama |
|---|---|---|
| bolgeId | Long | Kamera bölgesi |
| kameraAdi | String | Kamera adı |
| sonKareZamani | LocalDateTime | Son kare zamanı |
| fps | Double | FPS tahmini |

### DTO-9 : Diğer modeller (EKLENEN — özet)

BolgeDTO; KullaniciRequestDTO / KullaniciResponseDTO / KullaniciGuncelleRequestDTO; ProfilResponseDTO / ProfilGuncelleRequestDTO; SifreDegistirRequestDTO; PersonelDTO / PersonelRequestDTO / PersonelIstatistikDTO; PersonelGaleriDTO / PersonelYuzDTO / YuzYukleRequestDTO; KaliteIstatistikDTO; HaftalikRaporOzetDTO; IslemLogDTO; FinetuneHavuzSenkronDTO; KameraDurumDTO.

---

## AKSİYONLAR

### BACKEND SERVİSLERİ

| Tanım | Endpoint | REST Method | Request Model | Response Model |
|---|---|---|---|---|
| Kullanıcı adı/şifre ile giriş yapar, rol ve bölge bilgisini içeren JWT üretir | /api/auth/login | POST | LoginRequestDTO | LoginResponseDTO |
| Profil getirir / günceller / şifre değiştirir (EKLENEN) | /api/auth/profil, /api/auth/sifre | GET/PUT | Profil*/Sifre* | ProfilResponseDTO |
| Python AI Core servisinden gelen yeni ihlal kaydını sisteme işler | /api/ihlaller | POST | IhlalKayitRequestDTO | IhlalResponseDTO |
| JWT’deki role göre filtrelenmiş ihlal listesini getirir | /api/ihlaller | GET | - | List IhlalResponseDTO |
| Belirli bir ihlalin detayını getirir | /api/ihlaller/{id} | GET | - | IhlalResponseDTO |
| Yanlış pozitif tespiti Hatalı Tespit olarak işaretler | /api/ihlaller/{id}/reddet | POST | IhlalRedRequestDTO | IhlalResponseDTO |
| İhlali Çözüldü olarak kapatır (EKLENEN) | /api/ihlaller/{id}/coz | POST | IhlalCozRequestDTO | IhlalResponseDTO |
| Bölge ve ihlal tipi bazlı toplu istatistik getirir | /api/ihlaller/istatistik | GET | - | List IhlalIstatistikDTO |
| Personel bazlı istatistik getirir (EKLENEN) | /api/ihlaller/istatistik/personel | GET | - | List PersonelIstatistikDTO |
| Kalite istatistiği getirir (EKLENEN) | /api/ihlaller/istatistik/kalite | GET | - | KaliteIstatistikDTO |
| Fine-tune havuzunu senkronize eder (EKLENEN) | /api/ihlaller/finetune-havuz/senkronize | POST | - | FinetuneHavuzSenkronDTO |
| Tanımlı tüm üretim bölgelerini listeler | /api/bolgeler | GET | - | List BolgeDTO |
| Kullanıcı listeler / oluşturur / günceller | /api/kullanicilar | GET/POST/PUT | Kullanici*DTO | KullaniciResponseDTO |
| Personel listeler / oluşturur / günceller / yüz ekler (EKLENEN) | /api/personeller ... | GET/POST/PUT/DELETE | Personel*/Yuz* | Personel*/PersonelYuzDTO |
| Kamera heartbeat yazar / durum listeler (EKLENEN) | /api/kameralar/heartbeat, /durum | POST/GET | KameraHeartbeatDTO | KameraDurumDTO |
| Haftalık rapor özet / PDF (EKLENEN) | /api/raporlar/haftalik(.pdf) | GET | - | HaftalikRaporOzetDTO / PDF |
| Denetim loglarını listeler (EKLENEN) | /api/islem-loglari | GET | - | List IslemLogDTO |

---

## BİLEŞENLER

### COMPONENT-1 : LoginComponent

**Bileşen Tanımı:** Kullanıcı adı/şifre ile giriş formunu sunan, başarılı girişte JWT’yi tarayıcıda saklayıp kullanıcıyı rolüne göre ilgili panele yönlendiren giriş ekranı bileşenidir.

**Aksiyon Listesi:**
- Kullanıcı adı ve şifre alanlarını doğrular (boş bırakılamaz)
- /api/auth/login endpoint’ine istek atar
- Başarılı girişte JWT’yi saklar ve rolü AuthGuard’a iletir
- Rol ISG_YONETICI ise AdminDashboard’a, FORMEN ise ForemanDashboard’a, GORUNTULEYICI ise ViewerDashboard’a yönlendirir
- Hatalı girişte kullanıcıya uyarı mesajı gösterir

**Alt Bileşenler:** —

### COMPONENT-2 : AdminDashboardComponent

**Bileşen Tanımı:** İSG yöneticisinin fabrikanın tüm bölgelerine ait ihlal kanıtlarını, istatistik grafiklerini, kullanıcı yönetimini ve denetim günlüğünü görüntülediği üst yönetim paneli bileşenidir.

**Aksiyon Listesi:**
- AdminGuard ile yalnızca ISG_YONETICI rolüne erişim izni verir
- /api/ihlaller endpoint’inden filtresiz (tüm fabrika) veriyi çeker
- /api/ihlaller/istatistik ve kalite/personel istatistiklerini grafik bileşenlerine iletir
- İhlal reddetme (/reddet) ve çözme (/coz) aksiyonlarını tetikler
- Bölge ve ihlal tipine göre filtreleme yapar
- Kullanıcı yönetimi, denetim günlüğü, kamera durumu, haftalık rapor ve profil işlemlerini sunar (EKLENEN)

**Alt Bileşenler:** IhlalListesiComponent, IstatistikGrafikComponent, IhlalDetayModalComponent, KameraDurumPaneli, KaliteGrafik, DenetimGunlugu, KullaniciYonetimSayfasi, ProfilPaneli, PersonelIstatistikPaneli

### COMPONENT-3 : ForemanDashboardComponent

**Bileşen Tanımı:** Formenin yalnızca sorumlu olduğu bölge(ler)e ait risk takip panelini sunan bileşendir. JWT’deki bolgeIds ile kısıtlanır.

**Aksiyon Listesi:**
- ForemanGuard ile yalnızca FORMEN rolüne ve token’daki bolgeIds’e göre erişimi kısıtlar
- /api/ihlaller endpoint’inden yalnızca yetkili bölgelere ait veriyi çeker
- KPI kartları (aktif / bugünkü / risk) ve haftalık trend özetini gösterir (EKLENEN)
- “Çözüldü” işaretleme ve CSV dışa aktarma sağlar (EKLENEN)
- Başka bölge verisine erişim/istek göndermez

**Alt Bileşenler:** IhlalListesiComponent, IstatistikGrafikComponent, IhlalDetayModalComponent, PersonelIstatistikPaneli, BolgeSaatOzetPaneli, KameraDurumPaneli

### COMPONENT-4 : IhlalListesiComponent

**Bileşen Tanımı:** İhlal kayıtlarını tarih, bölge ve tip filtreleriyle tablo halinde listeleyen, panellerde ortak kullanılan (shared) bileşendir.

**Aksiyon Listesi:**
- Input olarak ihlal listesini ve kullanıcı rolünü alır
- Bir satıra tıklandığında IhlalDetayModalComponent’i açar
- Sayfalama (pagination) ve tarih/bölge bazlı sıralama sağlar

**Alt Bileşenler:** —

### COMPONENT-5 : IstatistikGrafikComponent

**Bileşen Tanımı:** Chart.js kullanarak ihlal tiplerinin (Baret, Yelek, Gözlük) yüzdelik dağılımını pasta grafik ile gösteren, rol bazlı veri kapsamına duyarlı görselleştirme bileşenidir.

**Aksiyon Listesi:**
- Input olarak IhlalIstatistikDTO listesini alır
- Pasta grafiği ve haftalık yüzde değişimini render eder
- Grafik üzerinde bölge/tip bazlı tıklanabilir filtre sağlar

**Alt Bileşenler:** —

### COMPONENT-6 : IhlalDetayModalComponent

**Bileşen Tanımı:** Seçilen ihlalin fotoğrafını, tespit zamanını, bölgesini ve personel bilgisini büyük görünümde sunan; yöneticiler için “Reddet”, formen/yönetici için “Çözüldü” aksiyonunu barındıran modal bileşendir.

**Aksiyon Listesi:**
- Seçilen ihlalin detayını büyük fotoğraf ile gösterir (AuthImgDirective ile JWT’li yükleme)
- ISG_YONETICI rolü için “Hatalı Tespit Olarak İşaretle” butonunu gösterir
- FORMEN / ISG_YONETICI için “Çözüldü” butonunu gösterir (EKLENEN)
- Reddet/çöz aksiyonlarında ilgili API çağrılarını yapar ve listeyi günceller

**Alt Bileşenler:** —

### COMPONENT-7 : ViewerDashboardComponent (EKLENEN)

**Bileşen Tanımı:** GORUNTULEYICI rolü için salt okunur üst yönetim / misafir panelidir. Reddet/çöz aksiyonları yoktur.

**Aksiyon Listesi:**
- ViewerGuard ile yalnızca GORUNTULEYICI erişimine izin verir
- İhlal listesi, istatistik ve kamera durumunu salt okunur gösterir

**Alt Bileşenler:** IhlalListesiComponent, IstatistikGrafikComponent, KameraDurumPaneli

### COMPONENT-8 : KameraDurumPaneli / ProfilPaneli / DenetimGunlugu / KullaniciYonetimSayfasi (EKLENEN)

**Bileşen Tanımı:** Kamera online/offline göstergesi; kullanıcı profil ve şifre yönetimi; islem_loglari denetim görünümü; yönetici kullanıcı CRUD ekranı.

**Aksiyon Listesi:**
- /api/kameralar/durum, /api/auth/profil, /api/islem-loglari, /api/kullanicilar uçlarını kullanır

**Alt Bileşenler:** —

### COMPONENT-9 : Public sayfalar — Anasayfa, Iletisim, UyelikBasvurusu, Basvurularim (EKLENEN)

**Bileşen Tanımı:** Extranet benzeri tanıtım ve demo başvuru sayfalarıdır. Panel yetkisi gerektirmez.

**Aksiyon Listesi:**
- /, /iletisim, /uyelik-basvurusu, /basvurularim rotalarını sunar
- Giriş ekranına yönlendirme sağlar

**Alt Bileşenler:** PanelShell, ExtranetFooter

---

## MODÜLLER

### MODÜL-1 : Yapay Zeka Görüntü İşleme ve Tespit Motoru (AI Core)

**Modül Tanımı:** Canlı kamera akışlarını anlık olarak okuyan, KDD ihlallerini tespit edip kanıt görsellerini üreten otonom Python servisidir.

**Aksiyon Listesi:**
- IP kamera/RTSP/HTTP/webcam/video kaynağını okur ve kare bazlı işler; kopunca yeniden bağlanır
- YOLO modeli ile kare üzerinde kişi, NO-Hardhat (BARET) ve NO-Safety Vest (YELEK) nesnelerini tespit eder
- IoU tracker ile aynı kişi üzerinde ihlal süresi biriktirir; eşik ve cooldown sonrası kayıt üretir (EKLENEN)
- Opsiyonel YuNet+SFace kişi tanıma ile personel eşlemesi yapar (EKLENEN)
- İhlal eşiği aşılınca kanıt karesini alır (yüz blur uygulanmaz — SİLİNEN davranış)
- Orijinal görseli base64 formatına çevirip IhlalKayitRequestDTO olarak Java API’sine POST eder
- Periyodik kamera heartbeat gönderir (EKLENEN)
- Çoklu kamera: cameras.json ile thread başına pipeline (EKLENEN)
- Test videoları ile offline test/kalibrasyon modu çalıştırabilir

**Alt Bileşenler:** main, config, pipeline, ppe_detector, tracker, stream, auth_client, backend_client, face_recognizer

### MODÜL-2 : Merkezi Veri Yönetimi ve API (Backend)

**Modül Tanımı:** Python servisinden gelen verileri işleyen, PostgreSQL veritabanı ilişkilerini kuran ve Angular arayüzüne RESTful uçlar sunan Java Spring Boot (Java 21) modülüdür.

**Aksiyon Listesi:**
- /api/ihlaller POST ucundan gelen isteği doğrular ve ihlaller tablosuna foreign key ilişkileriyle kaydeder
- Kanıt görsellerini dosya sistemine yazar, veritabanına yalnızca dosya yolunu işler
- /api/ihlaller GET ucunda JWT içindeki role göre sorguyu filtreler (Formen: bolgeIds, Yönetici/Görüntüleyici: filtresiz)
- /api/ihlaller/istatistik ucunda bölge/tip bazlı gruplama ve önceki haftaya göre yüzde değişim hesabı yapar
- /api/ihlaller/{id}/reddet ucunda durum alanını HATALI_TESPIT olarak günceller ve islem_loglari tablosuna kayıt düşer
- /api/ihlaller/{id}/coz ucunda durum alanını COZULDU olarak günceller (EKLENEN)
- Fine-tune havuzuna reddedilen görselleri kopyalar (EKLENEN)

**Alt Bileşenler:** —

### MODÜL-3 : Kimlik Doğrulama ve Rol Bazlı Erişim (JWT Security)

**Modül Tanımı:** Sisteme giriş yapacak kurumsal personelin kimliğini doğrulayan, JWT üreten ve kullanıcının rolüne göre veri erişim sınırlarını çizen güvenlik duvarıdır.

**Aksiyon Listesi:**
- /api/auth/login ucunda kullanıcı adı/şifre doğrulaması yapar (BCrypt hash karşılaştırması)
- Doğrulama başarılıysa kullanıcı id, rol, bolgeId ve bolgeIds bilgilerini claim olarak içeren JWT üretir
- Angular AuthGuard / AdminGuard / ForemanGuard / ViewerGuard her route değişiminde token’ın geçerliliğini kontrol eder
- HTTP Interceptor her isteğin Authorization header’ına Bearer token ekler
- Backend tarafında @PreAuthorize ile rol kontrolü yapılır; yetkisiz istek anında 403 Forbidden döner
- Başarısız giriş denemeleri islem_loglari’na yazılır (EKLENEN)

**Alt Bileşenler:** —

### MODÜL-4 : İSG Yöneticisi Tam Erişim Paneli (Admin Dashboard)

**Modül Tanımı:** Fabrikanın tüm bölgelerine ait ihlal verilerini kanıtlarla sunan, departmanlar arası risk kıyaslamasını sağlayan üst yönetim raporlama arayüzüdür.

**Aksiyon Listesi:**
- AdminGuard tetiklenerek yalnızca ISG_YONETICI rolüne erişim izni verilir
- Tüm fabrika verisi filtresiz çekilir ve tabloda kanıt fotoğraflarla sunulur
- İhlal tiplerinin fabrika geneli yüzdelik dağılımı pasta grafik ile gösterilir
- Yönetici “Reddet” aksiyonuyla yanlış pozitif tespitleri işaretleyebilir
- Kullanıcı yönetimi, denetim günlüğü, kalite istatistiği ve haftalık PDF rapor sunulur (EKLENEN)

**Alt Bileşenler:** IhlalListesiComponent, IstatistikGrafikComponent, IhlalDetayModalComponent

### MODÜL-5 : Formen/Bölge Şefi Takip Paneli (Restricted Dashboard)

**Modül Tanımı:** Yalnızca formenin sorumlu olduğu vardiya/bölge(ler) verilerini getiren, doğrudan kaza önleyici risk takip arayüzüdür.

**Aksiyon Listesi:**
- ForemanGuard tetiklenerek arayüz kendini formenin bolgeIds’i ile kısıtlar
- API yalnızca formenin yetkili olduğu bölgelere ait veriyi döner
- Amaç kişi avı değil risk analizi olduğundan, haftalık değişim yüzdesi ve KPI özeti sunulur
- “Çözüldü” ile saha müdahalesi kapatılır; CSV dışa aktarma yapılır (EKLENEN)

**Alt Bileşenler:** IhlalListesiComponent, IstatistikGrafikComponent

### MODÜL-6 : Olay Kaydı ve Hata Bildirim Yönetimi (Audit & Feedback)

**Modül Tanımı:** Yapay zekanın yapabileceği yanlış pozitif (False-Positive) tespitleri reddetmek, çözmek ve sistem üzerindeki kullanıcı işlemlerini loglamak için kurulan kalite kontrol modülüdür.

**Aksiyon Listesi:**
- Yönetici “Reddet” butonuna bastığında ihlaller.durum alanı HATALI_TESPIT olarak güncellenir
- Reddedilen kayıt istatistik sorgularından (/api/ihlaller/istatistik) otomatik olarak hariç tutulur
- İşlem, islem_loglari tablosuna kullanıcı, zaman ve ilgili ihlal id’siyle kaydedilir
- Reddedilen görseller YOLO modelinin yeniden eğitilmesi (fine-tuning) için `uploads/finetune-havuz/{tip}/` havuzuna kopyalanır

**Alt Bileşenler:** —

### MODÜL-7 : Kamera Sağlık İzleme (EKLENEN)

**Modül Tanımı:** AI Core heartbeat’leri ile kameraların çevrimiçi durumunu panelde gösteren izleme modülüdür.

**Aksiyon Listesi:**
- AI Core /api/kameralar/heartbeat ile durum yazar
- Panel KameraDurumPaneli online/offline gösterir

**Alt Bileşenler:** KameraDurumPaneli

### MODÜL-8 : Personel ve Kişi Tanıma (EKLENEN)

**Modül Tanımı:** Saha personeli kaydı, yüz galerisi ve AI Core kişi eşlemesini yöneten modüldür.

**Aksiyon Listesi:**
- Personel CRUD ve yüz yükleme API’lerini sunar
- AI Core galeriyi yükler / periyodik yeniler
- İhlalde personelId / personelSicilNo eşlemesi yapar

**Alt Bileşenler:** PersonelIstatistikPaneli, face_recognizer

### MODÜL-9 : Raporlama (EKLENEN)

**Modül Tanımı:** Haftalık ihlal özeti ve PDF indirme modülüdür.

**Aksiyon Listesi:**
- /api/raporlar/haftalik ve /haftalik.pdf uçlarını sunar
- İsteğe bağlı zamanlayıcı ile periyodik özet üretebilir

**Alt Bileşenler:** —
