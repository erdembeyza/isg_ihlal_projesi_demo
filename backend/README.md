# Backend (Java Spring Boot)

Bu klasör, MODÜL-2 (Merkezi Veri Yönetimi ve API) ve MODÜL-3 (Kimlik Doğrulama)
için Java Spring Boot projesini barındıracaktır.

Proje iskeleti **Faz 2**'de [start.spring.io](https://start.spring.io) üzerinden
şu bağımlılıklarla oluşturulacaktır:

- Spring Web
- Spring Data JPA
- Spring Security
- PostgreSQL Driver
- Validation
- Flyway Migration

> Not: Veritabanı migration dosyaları (`src/main/resources/db/migration/`) Faz 1
> kapsamında burada oluşturulmaya başlanmıştır; Spring Boot projesi Faz 2'de bu
> klasörün üzerine kurulacaktır.

## Veritabanı Migration'ları (Faz 1)

Şema, `tasarim_mimari.md` dokümanındaki 5 tablo ve tüm FK/UNIQUE/CHECK
kısıtları temel alınarak Flyway migration dosyalarıyla yönetilir:

- `V1__init.sql` — 5 tablo (`bolgeler`, `ihlal_tipleri`, `kullanicilar`,
  `ihlaller`, `islem_loglari`) ve tüm constraint'ler
- `V2__seed.sql` — BARET/YELEK/GOZLUK ihlal tipleri, örnek bölge, 1 admin +
  1 formen kullanıcısı (şifreler BCrypt ile hash'lenmiştir)

Backend projesi (Faz 2) henüz kurulmadığı için migration'lar şu an standalone
Flyway Docker imajı ile uygulanıyor:

```powershell
# repo kökünden
./scripts/flyway-migrate.ps1            # migrate (varsayılan)
./scripts/flyway-migrate.ps1 -Command info
```

Spring Boot projesi Faz 2'de `spring-boot-starter-data-jpa` + `flyway-core`
bağımlılıklarıyla oluşturulduğunda, aynı klasördeki migration'ları uygulama
ayağa kalkarken otomatik olarak (idempotent şekilde) çalıştıracaktır;
`flyway_schema_history` tablosu sayesinde zaten uygulanmış migration'lar
tekrar çalıştırılmaz.

**Dev/test giriş bilgileri** (yalnızca yerel ortam, production'da değiştirin):

| Kullanıcı adı | Şifre | Rol |
|---|---|---|
| `admin` | `Admin123!` | ISG_YONETICI |
| `formen1` | `Formen123!` | FORMEN (bolge_id=1) |
