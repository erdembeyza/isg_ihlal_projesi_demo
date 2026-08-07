# 10 Dakikalık Konuşma Metni

**Sunum:** İSG Kural İhlal Tespit ve Uyarı Sistemi  
**Dosya:** `Beyza_Erdem_ISG_Ihlal_Tespit_Sistemi.pptx`  
**Süre hedefi:** 9:30–10:00 (sorular ayrı)

> Okuma hızı: sakin, net diksiyon. Slayt başına yaklaşık süre sağda.

---

## 0:00–0:30 · Kapak

Merhaba, ben **Beyza Erdem**. Bu sunumda Erdemir üretim sahaları için geliştirdiğim **İSG Kural İhlal Tespit ve Uyarı Sistemi**ni anlatacağım.

Tek cümleyle: mevcut güvenlik kameralarını kullanarak baret ve yelek gibi kişisel koruyucu donanım ihlallerini yapay zekâ ile tespit eden, kaydeden ve yetkili personele web paneli üzerinden ulaştıran uçtan uca bir sistem.

---

## 0:30–1:00 · Gündem

Altı başlıkta ilerleyeceğim: problem, çözüm, mimari ve akış, İSG farkındalığı, fabrika bağlantısı, sonuç ve yol haritası. Yaklaşık on dakikada tamamlayacağım.

---

## 1:00–2:15 · Problem (~75 sn)

Demir-çelik üretimi yüksek riskli bir ortamdır. Sıcak ve soğuk haddehane gibi sahalarda **KKD** — yani baret, yelek, gözlük — eksikliği ciddi iş kazasına yol açabilir.

Bugün sahada kameralar var; ancak 7/24 manuel izlemek formenin zamanını alır. Geç fark edilen ihlal, geç müdahale demektir. Ayrıca ihlalin zamanı, bölgesi ve kanıt fotoğrafı sistematik kayıt altında olmalıdır.

Bu yüzden hedefim şuydu: **yeni kamera yatırımı olmadan**, mevcut altyapıyla ihlalleri proaktif ve otomatik yakalamak.

---

## 2:15–3:15 · Çözüm (~60 sn)

Çözüm dört adımda özetleniyor:

1. Mevcut kameralardan görüntü alınır — RTSP veya IP Webcam.  
2. **YOLOv8 Nano** modeli kareleri analiz eder; baret/yelek eksikliğini tespit eder.  
3. **Spring Boot** backend ihlali JWT güvenliğiyle kaydeder.  
4. **Angular** web panelinde İSG yöneticisi ve formen aksiyon alır.

Ek olarak haftalık PDF rapor ve isteğe bağlı Telegram uyarısı var. Sistem bölge bazlı formen erişimiyle Erdemir saha organizasyonuna uyumludur.

---

## 3:15–4:45 · Mimari (~90 sn)

Üç katmanlı mimari:

- **AI Core:** Python, YOLOv8, OpenCV. Kamera akışını okur, KKD sınıflarını bulur, yaklaşık **8 saniyelik** süre eşiğiyle yanlış alarmı azaltır, kanıt fotoğrafını gönderir.  
- **Backend:** Java 21, Spring Boot, PostgreSQL, Flyway. Kimlik doğrulama, ihlal yaşam döngüsü, kamera heartbeat, denetim günlüğü, rapor API.  
- **Frontend:** Angular 22, ErdemirOnline benzeri arayüz. Yönetici tüm fabrikayı, formen kendi bölgesini, görüntüleyici salt okunur şekilde izler.

Faz 0’dan Faz 8’e kadar uçtan uca entegrasyon tamamlandı.

---

## 4:45–6:00 · Tespit akışı (~75 sn)

Akış şöyle:

Kamera karesi gelir → YOLOv8 her N karede PPE sınıflarına bakar → `NO-Hardhat` / `NO-Safety Vest` kişi kutusuyla eşlenir → IoU tracker süre biriktirir → eşik aşılınca `POST /api/ihlaller` ile fotoğraf gider → panelde **Aktif** görünür → formen **Çözüldü** işaretler veya yönetici yanlışsa **Hatalı tespit** der.

Hatalı tespitler fine-tune havuzuna düşer; yani sistem kendi kalitesini iyileştirmeye de açık.

---

## 6:00–7:15 · İSG & KKD (~75 sn)  ★ Değerlendirme Bölüm B

Bu proje yalnızca yazılım değil; **İş Sağlığı ve Güvenliği** disiplinini destekler.

- **Baret:** düşen cisim ve kafa travması riskine karşı.  
- **Yelek:** saha görünürlüğü.  
- **Gözlük:** sıçrama, toz, kıvılcım riski — sınıf haritası hazır; Erdemir saha verisiyle fine-tune ile güçlendirilecek.

Güvenli çalışma açısından kritik nokta: sistem insanı dışlamaz. Formen sahada müdahale eder; İSG yöneticisi fabrika genelini izler. Yanlış alarmlar ayıklanır; böylece hem güven hem güvenilirlik korunur.

---

## 7:15–8:15 · Fabrika bağlantısı (~60 sn)  ★ Değerlendirme Bölüm C

Sistemi soyut bir demo olarak bırakmadım; **Erdemir saha diline** bağladım.

Demo bölgeler: 1. Sıcak Haddehane, 1. Soğuk Haddehane, Veri Merkezi. Çoklu kamera ile PC, telefon ve tablet akışı destekleniyor.

Roller gerçek iş sürecine karşılık geliyor:

- İSG yöneticisi → tüm fabrika, rapor, kullanıcı yönetimi  
- Formen → kendi bölgesinde çözümleme  
- Görüntüleyici → üst yönetim takibi  

Yani öğrenilen prosesi kendi kelimelerimle; gözlemleri iş sürecine bağlayarak tasarladım.

---

## 8:15–9:15 · Panel değeri + kazanımlar (~60 sn)

Panelde operasyonel değer net:

Canlı ihlal listesi, KPI ve trend, kamera sağlığı, haftalık PDF, denetim günlüğü, fine-tune döngüsü.

**Kazanım:** sıfır yeni kamera, rol bazlı erişim, uçtan uca çalışan ürün.  
**Dürüst sınır:** gözlük için saha etiketi gerekir; genel PPE modeli Erdemir sahasına fine-tune ile daha da isabetli olur; yüz tanıma bilerek kapsam dışı.  
**Sonraki adım:** saha verisiyle fine-tune, üretim RTSP sertleştirmesi, İSG prosedürlerine resmi entegrasyon.

---

## 9:15–10:00 · Kapanış + motivasyon (~45 sn)  ★ Kariyer

Özetle: Erdemir sahalarında mevcut kameralarla, YOLOv8 ile baret ve yelek ihlallerini gerçek zamanlı yakalayan; formene ve İSG yöneticisine raporlayan uçtan uca bir İSG dijitalleşme çözümüdür.

Demir-çelik sektörü; yüksek proses karmaşıklığı ile İSG disiplininin bir arada olduğu nadir alanlardan biri. Bu stajda edindiğim saha bağlamını yazılım ve yapay zekâ ile birleştirerek Erdemir’de güvenli, veriye dayalı üretime katkı sunmak istiyorum.

Dinlediğiniz için teşekkür ederim. Sorularınızı alabilirim.

---

## Soru-cevap için hazır cevaplar

| Olası soru | Kısa cevap |
|---|---|
| Gözlük neden zayıf? | Kullanılan Construction Site Safety veri setinde gözlük sınıfı yok/yetersiz; harita hazır, saha etiketi + fine-tune ile eklenir. |
| Yanlış alarm nasıl azalır? | ~8 sn süre eşiği + IoU tracker + Hatalı tespit → fine-tune havuzu. |
| KVKK? | Kanıt fotoğrafı yetkili rollere; yüz tanıma yok. Üretimde saklama politikası İSG/KVKK ile netleştirilir. |
| Neden YOLO Nano? | Edge/CPU’da düşük gecikme; saha için hız-doğruluk dengesi. Fine-tune sonrası aynı aile büyütülebilir. |
| Formen ne yapar? | Kendi bölgesindeki Aktif ihlali görür, sahada uyarır, Çözüldü + not yazar. |
| Yeni kamera gerekir mi? | Hayır; mevcut RTSP / IP kamera yeter. |

---

## Sunum günü kontrol listesi

- [ ] PPTX açıldı, slayt geçişleri çalışıyor  
- [ ] Canlı demo hazırsa: kısa video loop + panel (admin) yedek plan  
- [ ] Demo yoksa: slayt 6–9 ile akış anlatımı yeterli  
- [ ] Kronometre: 9:30’da kapanışa geç  
- [ ] KKD / haddehane / formen terimlerini bilinçli kullan  
- [ ] Son slaytta kariyer cümlesini acele etmeden söyle  
