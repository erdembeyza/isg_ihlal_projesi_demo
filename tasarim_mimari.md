# İSG KURAL İHLAL TESPİT VE UYARI SİSTEMİ – TASARIM SÜRECİ DOKÜMANI

**SORUMLU:** Beyza Erdem

---

## GENEL AÇIKLAMALAR

### GENEL TANIMLAR

- Amaç, Erdemir üretim sahalarında baret, gözlük veya yelek (KDD) takmayan personelin gerçek zamanlı olarak tespit edilerek olası iş kazalarının kaza yaşanmadan önlenmesidir.
- Sistem üç ana katmandan oluşur: (1) canlı kamera görüntüsünü işleyen ve KDD (baret, yelek, gözlük) ihlallerini tespit eden Python/OpenCV/YOLO tabanlı Yapay Zeka Görüntü İşleme servisi (AI Core), (2) verileri kalıcı hale getiren ve yetki bazlı erişim sunan Java Spring Boot tabanlı RESTful API (Backend), (3) kullanıcıların bulgularla etkileşime girdiği Angular tabanlı web arayüzü (Frontend).
- Temel amaç, üretim sahasındaki KDD ihlallerini insan müdahalesi olmadan, gerçek zamanlı ve mevcut kamera altyapısına sıfır donanım maliyetiyle tespit ederek olası bir iş kazasını proaktif olarak önlemektir.
- KVKK gereği her ihlal iki fotoğraf versiyonuyla (orijinal ve yüzü blurlanmış) kaydedilir; formen rolündeki kullanıcılar yalnızca kendi bölgelerinin blurlu kanıtlarını, İSG yöneticisi rolündeki kullanıcılar ise fabrikanın tamamının sansürsüz kanıtlarını görebilir.
- Bu doküman, geliştirme ekibinin tek referans kaynağı olacak şekilde; veritabanı tabloları ve kısıtları (constraints), API request/response modelleri (DTO), backend endpoint listesi, frontend bileşen hiyerarşisi ve her modülün somut aksiyon listesini bir arada sunar.

### DİĞER AÇIKLAMALAR

- Kimlik doğrulama ve yetkilendirme JWT (JSON Web Token) ile yapılır. Sistemde iki rol tanımlıdır: ISG_YONETICI (tüm fabrika, orijinal fotoğraflar) ve FORMEN (yalnızca kendi bölgesi, blurlu fotoğraflar). Yetkisiz erişim denemeleri backend tarafında 403 Forbidden ile engellenir.
- Veritabanı olarak PostgreSQL kullanılacaktır; bölge, kullanıcı, ihlal tipi ve ihlal kayıtları birbirine foreign key ilişkileriyle bağlı ilişkisel bir model üzerinde tutulur.
- Görüntü işleme tarafı Python, OpenCV ve **YOLOv8 Nano (kaynak tüketimini minimize eden hafif pre-trained model)** ile gerçekleştirilir; yüz bölgesi tespit edildikten sonra cv2.GaussianBlur fonksiyonu ile sansürleme (blur) işlemi otomatik olarak uygulanır.
- Test ve entegrasyon aşamasında gerçek kamera akışı yerine Kaggle üzerindeki açık kaynak İSG kural ihlali videoları ve önceden yapılandırılmış mock veritabanı kayıtları kullanılacaktır; bu sayede canlı kamera altyapısı olmadan da uçtan uca test yapılabilecektir.
- Sistem, kamera/bölge sayısı arttıkça yatay olarak ölçeklenebilecek şekilde tasarlanır; Python tarafı bağımsız worker süreçleri olarak çoğaltılabilir, Backend ve veritabanı katmanı bu artışı bölge bazlı foreign key yapısıyla karşılayabilir.
- Sıfır donanım maliyeti hedefi gereği sistem yalnızca yazılım katmanında konumlanır; mevcut IP kameralardan görüntü akışı RTSP/HTTP protokolleri üzerinden okunur, ek donanım (yeni kamera, sunucu vb.) yatırımı gerektirmez.
- Yapay zekanın üretebileceği yanlış pozitif (false-positive) tespitler için bir denetim/geri bildirim mekanizması (MODÜL-8/MODÜL-6) tasarlanmıştır; reddedilen kayıtlar hem istatistiklerden düşer hem de ileride modelin yeniden eğitilmesi (fine-tuning) için veri seti oluşturur.

---

## VERİ TABANI

### TABLO-1 : bolgeler

**Tablo Tanımı:** Fabrika içindeki üretim bölgelerini (vardiya/departman) tanımlayan referans tablodur. Formen yetkilendirmesi ve ihlal kayıtlarının konumlandırılması bu tabloya bağlı bolge_id üzerinden yapılır.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Bölge birincil anahtarı |
| bolge_adi | VARCHAR(100) | NOT NULL | - | Bölge/vardiya adı (ör. Yüksek Fırın-1) |
| aciklama | VARCHAR(255) | NULL | - | Bölgeye ait ek açıklama |

### TABLO-2 : ihlal_tipleri

**Tablo Tanımı:** Tespit edilebilecek KDD (Kişisel Koruyucu Donanım) ihlal tiplerini tanımlayan referans/lookup tablodur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | SMALLINT | NOT NULL | PK | İhlal tipi birincil anahtarı |
| tip_adi | VARCHAR(50) | NOT NULL | - | BARET / YELEK / GOZLUK |
| aciklama | VARCHAR(255) | NULL | - | İhlal tipine ait ek açıklama |

### TABLO-3 : kullanicilar

**Tablo Tanımı:** Sisteme giriş yapacak İSG yöneticisi ve formen rolündeki kurumsal personeli tutan tablodur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Kullanıcı birincil anahtarı |
| kullanici_adi | VARCHAR(50) | NOT NULL | - | Benzersiz giriş adı |
| sifre_hash | VARCHAR(255) | NOT NULL | - | BCrypt ile şifrelenmiş parola |
| ad_soyad | VARCHAR(100) | NOT NULL | - | Kullanıcının adı soyadı |
| rol | VARCHAR(20) | NOT NULL | - | ISG_YONETICI / FORMEN |
| bolge_id | BIGINT | NULL | FK | bolgeler.id — yalnızca FORMEN rolü için doludur |
| aktif_mi | BOOLEAN | NOT NULL | - | Kullanıcının aktif/pasif durumu (varsayılan: true) |

### TABLO-4 : ihlaller

**Tablo Tanımı:** Python AI Core servisi tarafından tespit edilen her bir KDD ihlalinin kanıt fotoğrafları, konumu, zamanı ve inceleme durumu ile kaydedildiği sistemin ana işlem (transactional) tablosudur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | İhlal kaydı birincil anahtarı |
| bolge_id | BIGINT | NOT NULL | FK | bolgeler.id — ihlalin tespit edildiği bölge |
| ihlal_tipi_id | SMALLINT | NOT NULL | FK | ihlal_tipleri.id — tespit edilen ihlalin tipi |
| tespit_zamani | TIMESTAMP | NOT NULL | - | AI Core'un ihlali tespit ettiği an |
| orijinal_foto_yolu | VARCHAR(500) | NOT NULL | - | Sansürsüz kanıt fotoğrafının depolama yolu/URL'i |
| blurlu_foto_yolu | VARCHAR(500) | NOT NULL | - | Yüzü blurlanmış kanıt fotoğrafının depolama yolu/URL'i |
| durum | VARCHAR(20) | NOT NULL | - | AKTIF / HATALI_TESPIT (varsayılan: AKTIF) |
| reddeden_kullanici_id | BIGINT | NULL | FK | kullanicilar.id — kaydı hatalı tespit olarak işaretleyen yönetici |
| red_zamani | TIMESTAMP | NULL | - | Kaydın hatalı tespit olarak işaretlendiği an |
| olusturma_zamani | TIMESTAMP | NOT NULL | - | Kaydın veritabanına yazıldığı an (varsayılan: now()) |

### TABLO-5 : islem_loglari

**Tablo Tanımı:** Kullanıcıların sistem üzerinde gerçekleştirdiği kritik işlemleri (giriş, ihlal reddetme vb.) izlenebilirlik ve denetim amacıyla kaydeden log tablosudur.

| Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama |
|---|---|---|---|---|
| id | BIGINT | NOT NULL | PK | Log kaydı birincil anahtarı |
| kullanici_id | BIGINT | NOT NULL | FK | kullanicilar.id — işlemi yapan kullanıcı |
| islem_tipi | VARCHAR(50) | NOT NULL | - | GIRIS / IHLAL_REDDETME / IHLAL_GORUNTULEME vb. |
| ilgili_ihlal_id | BIGINT | NULL | FK | ihlaller.id — işlemin ilişkili olduğu ihlal kaydı (varsa) |
| islem_zamani | TIMESTAMP | NOT NULL | - | İşlemin gerçekleştiği an |
| detay | VARCHAR(255) | NULL | - | İşleme dair serbest metin açıklama |

### DB CONSTRAINTS

| Kısıt Adı | Kısıt Tipi | Tablo | Tanım |
|---|---|---|---|
| fk_ihlal_bolge | FOREIGN KEY | ihlaller | ihlaller.bolge_id → bolgeler.id (ON DELETE RESTRICT) |
| fk_ihlal_tip | FOREIGN KEY | ihlaller | ihlaller.ihlal_tipi_id → ihlal_tipleri.id |
| fk_ihlal_red_kullanici | FOREIGN KEY | ihlaller | ihlaller.reddeden_kullanici_id → kullanicilar.id (NULL olabilir) |
| fk_kullanici_bolge | FOREIGN KEY | kullanicilar | kullanicilar.bolge_id → bolgeler.id (yalnızca FORMEN için dolu) |
| uq_kullanici_adi | UNIQUE | kullanicilar | kullanici_adi alanı benzersiz olmalıdır |
| ck_kullanici_rol | CHECK | kullanicilar | rol IN ('ISG_YONETICI','FORMEN') |
| ck_ihlal_durum | CHECK | ihlaller | durum IN ('AKTIF','HATALI_TESPIT') |
| fk_log_kullanici | FOREIGN KEY | islem_loglari | islem_loglari.kullanici_id → kullanicilar.id |
| fk_log_ihlal | FOREIGN KEY | islem_loglari | islem_loglari.ilgili_ihlal_id → ihlaller.id (NULL olabilir) |

---

## VERİ MODELLERİ

### DTO-1 : IhlalKayitRequestDTO

**Model Tanımı:** Python AI Core servisinin tespit ettiği bir ihlali Java Backend API'sine iletmek için POST isteğinde kullandığı model.

| Alan | Tip | Açıklama |
|---|---|---|
| bolgeId | Long | İhlalin tespit edildiği bölgenin kimliği |
| ihlalTipiId | Integer | Tespit edilen ihlal tipinin kimliği (baret/yelek/gözlük) |
| tespitZamani | LocalDateTime | İhlalin tespit edildiği an (ISO-8601) |
| orijinalFotoBase64 | String | Sansürsüz kanıt fotoğrafının base64 kodlu içeriği |
| blurluFotoBase64 | String | Yüzü blurlanmış kanıt fotoğrafının base64 kodlu içeriği |

### DTO-2 : IhlalResponseDTO

**Model Tanımı:** Frontend'e ihlal listesi/detayı döndürülürken kullanılan, kullanıcının rolüne göre foto alanı otomatik seçilen model.

| Alan | Tip | Açıklama |
|---|---|---|
| id | Long | İhlal kaydının kimliği |
| bolgeAdi | String | İhlalin tespit edildiği bölgenin adı |
| ihlalTipiAdi | String | Tespit edilen ihlal tipinin adı |
| tespitZamani | LocalDateTime | İhlalin tespit edildiği an |
| fotoUrl | String | Role göre orijinal ya da blurlu fotoğrafın erişim adresi |
| durum | String | AKTIF / HATALI_TESPIT |

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
| rol | String | ISG_YONETICI / FORMEN |
| adSoyad | String | Kullanıcının adı soyadı |
| bolgeId | Long | Kullanıcının sorumlu olduğu bölge kimliği (FORMEN için dolu, yönetici için null) |

### DTO-5 : IhlalIstatistikDTO

**Model Tanımı:** Dashboard'lardaki pasta grafik ve trend özetlerinde kullanılan, bölge/tip bazlı toplu istatistik modeli.

| Alan | Tip | Açıklama |
|---|---|---|
| bolgeAdi | String | İstatistiğin ait olduğu bölge |
| ihlalTipiAdi | String | İstatistiğin ait olduğu ihlal tipi |
| toplamAdet | Integer | Seçilen periyottaki toplam ihlal adedi |
| yuzdeDegisim | Double | Önceki haftaya göre yüzdesel değişim (ör. +20.0) |

### DTO-6 : IhlalRedRequestDTO

**Model Tanımı:** İSG yöneticisinin yanlış pozitif bir tespiti reddederken gönderdiği model.

| Alan | Tip | Açıklama |
|---|---|---|
| ihlalId | Long | Hatalı olduğu düşünülen ihlal kaydının kimliği |
| redNedeni | String | Reddetme gerekçesine dair opsiyonel açıklama |

---

## AKSİYONLAR

### BACKEND SERVİSLERİ

| Tanım | Endpoint | REST Method | Request Model | Response Model |
|---|---|---|---|---|
| Kullanıcı adı/şifre ile giriş yapar, rol ve bölge bilgisini içeren JWT üretir | /api/auth/login | POST | LoginRequestDTO | LoginResponseDTO |
| Python AI Core servisinden gelen yeni ihlal kaydını sisteme işler | /api/ihlaller | POST | IhlalKayitRequestDTO | IhlalResponseDTO |
| JWT'deki role göre filtrelenmiş ihlal listesini getirir (Formen: kendi bölgesi + blurlu, Yönetici: tüm fabrika + orijinal) | /api/ihlaller | GET | - | List\<IhlalResponseDTO\> |
| Belirli bir ihlalin detayını (fotoğraf, zaman, bölge, durum) getirir | /api/ihlaller/{id} | GET | - | IhlalResponseDTO |
| Yanlış pozitif tespiti "Hatalı Tespit" olarak işaretler ve istatistiklerden düşürür | /api/ihlaller/{id}/reddet | POST | IhlalRedRequestDTO | IhlalResponseDTO |
| Bölge ve ihlal tipi bazlı toplu istatistik ile haftalık trend verisini getirir | /api/ihlaller/istatistik | GET | - | List\<IhlalIstatistikDTO\> |
| Tanımlı tüm üretim bölgelerini listeler | /api/bolgeler | GET | - | List\<BolgeDTO\> |
| Yeni formen/kullanıcı tanımlar (yalnızca İSG yöneticisi yetkilidir) | /api/kullanicilar | POST | KullaniciRequestDTO | KullaniciResponseDTO |

---

## BİLEŞENLER

### COMPONENT-1 : LoginComponent

**Bileşen Tanımı:** Kullanıcı adı/şifre ile giriş formunu sunan, başarılı girişte JWT'yi tarayıcıda saklayıp kullanıcıyı rolüne göre ilgili panele yönlendiren giriş ekranı bileşenidir.

**Aksiyon Listesi:**
- Kullanıcı adı ve şifre alanlarını doğrular (boş bırakılamaz)
- /api/auth/login endpoint'ine istek atar
- Başarılı girişte JWT'yi saklar ve rolü AuthGuard'a iletir
- Rol ISG_YONETICI ise AdminDashboardComponent'e, FORMEN ise ForemanDashboardComponent'e yönlendirir
- Hatalı girişte kullanıcıya uyarı mesajı gösterir

**Alt Bileşenler:** —

### COMPONENT-2 : AdminDashboardComponent

**Bileşen Tanımı:** İSG yöneticisinin fabrikanın tüm bölgelerine ait orijinal (sansürsüz) ihlal kanıtlarını ve istatistik grafiklerini görüntülediği üst yönetim paneli bileşenidir.

**Aksiyon Listesi:**
- AdminGuard ile yalnızca ISG_YONETICI rolüne erişim izni verir
- /api/ihlaller endpoint'inden filtresiz (tüm fabrika) veriyi çeker
- /api/ihlaller/istatistik'ten pasta grafik verisini alır ve IstatistikGrafikComponent'e iletir
- İhlal reddetme aksiyonunu (/api/ihlaller/{id}/reddet) tetikler
- Bölge ve ihlal tipine göre filtreleme yapar

**Alt Bileşenler:**
- IhlalListesiComponent
- IstatistikGrafikComponent
- IhlalDetayModalComponent

### COMPONENT-3 : ForemanDashboardComponent

**Bileşen Tanımı:** Formenin yalnızca sorumlu olduğu bölgeye ait, işçi yüzlerinin blurlu gösterildiği risk takip panelini sunan bileşendir.

**Aksiyon Listesi:**
- ForemanGuard ile yalnızca FORMEN rolüne ve token'daki bolgeId'ye göre erişimi kısıtlar
- /api/ihlaller endpoint'inden yalnızca kendi bolge_id'sine ait blurlu veriyi çeker
- Haftalık trend özetini (ör. "Bu hafta gözlük takmama oranı %20 arttı") yönlendirici bir metin olarak gösterir
- Orijinal fotoğraf URL'ine hiçbir koşulda erişim/istek göndermez

**Alt Bileşenler:**
- IhlalListesiComponent
- IstatistikGrafikComponent

### COMPONENT-4 : IhlalListesiComponent

**Bileşen Tanımı:** İhlal kayıtlarını tarih, bölge ve tip filtreleriyle tablo halinde listeleyen, hem yönetici hem de formen panelinde ortak kullanılan (shared) bileşendir.

**Aksiyon Listesi:**
- Input olarak ihlal listesini ve kullanıcı rolünü alır
- Bir satıra tıklandığında IhlalDetayModalComponent'i açar
- Sayfalama (pagination) ve tarih/bölge bazlı sıralama sağlar

**Alt Bileşenler:** —

### COMPONENT-5 : IstatistikGrafikComponent

**Bileşen Tanımı:** Chart.js kullanarak ihlal tiplerinin (Baret, Yelek, Gözlük, Telefon) yüzdelik dağılımını pasta grafik ile gösteren, rol bazlı veri kapsamına duyarlı görselleştirme bileşenidir.

**Aksiyon Listesi:**
- Input olarak IhlalIstatistikDTO listesini alır
- Pasta grafiği ve haftalık yüzde değişimini render eder
- Grafik üzerinde bölge/tip bazlı tıklanabilir filtre sağlar

**Alt Bileşenler:** —

### COMPONENT-6 : IhlalDetayModalComponent

**Bileşen Tanımı:** Seçilen ihlalin fotoğrafını (role göre orijinal veya blurlu), tespit zamanını ve bölgesini büyük görünümde sunan; yöneticiler için "Reddet" aksiyonunu barındıran modal bileşendir.

**Aksiyon Listesi:**
- Seçilen ihlalin detayını büyük fotoğraf ile gösterir
- ISG_YONETICI rolü için "Hatalı Tespit Olarak İşaretle" butonunu gösterir
- Reddet aksiyonunda /api/ihlaller/{id}/reddet çağrısını yapar ve listeyi günceller

**Alt Bileşenler:** —

---

## MODÜLLER

### MODÜL-1 : Yapay Zeka Görüntü İşleme ve Tespit Motoru (AI Core)

**Modül Tanımı:** Canlı kamera akışlarını anlık olarak okuyan, KDD (Kişisel Koruyucu Donanım) ihlallerini tespit edip kanıt görsellerini kesen ve sansürleyen otonom Python servisidir.

**Aksiyon Listesi:**
- IP kamera/RTSP akışını saniyede 30 FPS hızında okur ve kare (frame) bazlı işler
- YOLO pre-trained modeli ile kare üzerinde kişi, baret, yelek ve gözlük nesnelerini tespit eder
- İhlal (nesne eksikliği) tespit edildiği milisaniyede ilgili karenin anlık görüntüsünü (snapshot) alır
- Yüz bölgesi koordinatlarını tespit edip cv2.GaussianBlur ile bulanıklaştırılmış ikinci bir kopya üretir
- Orijinal ve blurlu görselleri base64 formatına çevirip IhlalKayitRequestDTO olarak Java API'sine POST eder
- Kaggle test videoları ile offline test/kalibrasyon modu çalıştırabilir

**Alt Bileşenler:** —

### MODÜL-2 : Merkezi Veri Yönetimi ve API (Backend)

**Modül Tanımı:** Python servisinden gelen verileri işleyen, PostgreSQL veritabanı ilişkilerini kuran ve Angular arayüzüne RESTful uçlar sunan Java Spring Boot modülüdür.

**Aksiyon Listesi:**
- /api/ihlaller POST ucundan gelen isteği doğrular ve ihlaller tablosuna bolge_id, ihlal_tipi_id foreign key ilişkileriyle kaydeder
- Kanıt görsellerini (orijinal/blurlu) dosya sistemine/nesne depolamaya yazar, veritabanına yalnızca dosya yolunu işler
- /api/ihlaller GET ucunda JWT içindeki role göre sorguyu filtreler (Formen: WHERE bolge_id=…, Yönetici: filtresiz)
- /api/ihlaller/istatistik ucunda bölge/tip bazlı gruplama ve önceki haftaya göre yüzde değişim hesabı yapar
- /api/ihlaller/{id}/reddet ucunda durum alanını HATALI_TESPIT olarak günceller ve islem_loglari tablosuna kayıt düşer

**Alt Bileşenler:** —

### MODÜL-3 : Kimlik Doğrulama ve Rol Bazlı Erişim (JWT Security)

**Modül Tanımı:** Sisteme giriş yapacak kurumsal personelin kimliğini doğrulayan, JWT üreten ve kullanıcının rolüne göre (ISG_YONETICI, FORMEN) veri erişim sınırlarını çizen güvenlik duvarıdır.

**Aksiyon Listesi:**
- /api/auth/login ucunda kullanıcı adı/şifre doğrulaması yapar (BCrypt hash karşılaştırması)
- Doğrulama başarılıysa kullanıcı id, rol ve bolge_id bilgilerini claim olarak içeren JWT üretir
- Angular AuthGuard her route değişiminde token'ın geçerliliğini kontrol eder
- HTTP Interceptor her isteğin Authorization header'ına Bearer token ekler
- Backend tarafında @PreAuthorize ile rol kontrolü yapılır; yetkisiz istek anında 403 Forbidden döner

**Alt Bileşenler:** —

### MODÜL-4 : İSG Yöneticisi Tam Erişim Paneli (Admin Dashboard)

**Modül Tanımı:** Fabrikanın tüm bölgelerine ait ihlal verilerini orijinal (sansürsüz) kanıtlarla sunan, departmanlar arası risk kıyaslamasını sağlayan üst yönetim raporlama arayüzüdür.

**Aksiyon Listesi:**
- AdminGuard tetiklenerek yalnızca ISG_YONETICI rolüne erişim izni verilir
- Tüm fabrika verisi filtresiz çekilir ve tabloda orijinal fotoğraflarla sunulur
- İhlal tiplerinin (Baret, Yelek, Telefon) fabrika geneli yüzdelik dağılımı pasta grafik ile gösterilir
- Yönetici "Reddet" aksiyonuyla yanlış pozitif tespitleri işaretleyebilir

**Alt Bileşenler:**
- IhlalListesiComponent
- IstatistikGrafikComponent
- IhlalDetayModalComponent

### MODÜL-5 : Formen/Bölge Şefi Takip Paneli (Restricted Dashboard)

**Modül Tanımı:** Yalnızca formenin sorumlu olduğu vardiya/bölge verilerini getiren, işçi yüzlerinin blurlu gösterildiği doğrudan kaza önleyici risk takip arayüzüdür.

**Aksiyon Listesi:**
- ForemanGuard tetiklenerek arayüz kendini formenin bolge_id'si ile kısıtlar
- API yalnızca formenin yetkili olduğu bölgeye ait blurlu veriyi döner
- Amaç kişi avı değil risk analizi olduğundan, haftalık değişim yüzdesi yönlendirici bir özet metni olarak sunulur

**Alt Bileşenler:**
- IhlalListesiComponent
- IstatistikGrafikComponent

### MODÜL-6 : Olay Kaydı ve Hata Bildirim Yönetimi (Audit & Feedback)

**Modül Tanımı:** Yapay zekanın yapabileceği yanlış pozitif (False-Positive) tespitleri reddetmek ve sistem üzerindeki kullanıcı işlemlerini loglamak için kurulan kalite kontrol modülüdür.

**Aksiyon Listesi:**
- Yönetici "Reddet" butonuna bastığında ihlaller.durum alanı HATALI_TESPIT olarak güncellenir
- Reddedilen kayıt istatistik sorgularından (/api/ihlaller/istatistik) otomatik olarak hariç tutulur
- İşlem, islem_loglari tablosuna kullanıcı, zaman ve ilgili ihlal id'siyle kaydedilir
- Reddedilen görseller, ileriki fazlarda YOLO modelinin Erdemir'in koşullarına göre yeniden eğitilmesi (fine-tuning) için ayrı bir veri seti havuzuna işaretlenir

**Alt Bileşenler:** —
