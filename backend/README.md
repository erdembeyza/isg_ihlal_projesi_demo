# Backend (Java Spring Boot)

MODÜL-2 (Merkezi Veri Yönetimi ve API), MODÜL-3 (JWT kimlik doğrulama) ve
MODÜL-6 (reddetme + audit + fine-tune havuzu) implementasyonu.

- Java 21, Spring Boot, Spring Security (JWT), Spring Data JPA, Flyway, PostgreSQL

## Çalıştırma

1. Postgres ayağa kalkmış olmalı (`docker compose up -d` — repo kökünden).
2. Ortam değişkenleri için `backend/.env.example` dosyasına bakın.
3. Backend'i başlatın:

```powershell
cd backend
.\mvnw.cmd spring-boot:run
```

API: `http://localhost:8080` — Flyway migration'ları (V1–V5) açılışta uygulanır.

Standalone Flyway (opsiyonel):

```powershell
# repo kökünden
./scripts/flyway-migrate.ps1
./scripts/flyway-migrate.ps1 -Command info
```

## Migration'lar

| Dosya | İçerik |
|---|---|
| `V1__init.sql` | 5 tablo + constraint'ler |
| `V2__seed.sql` | BARET/YELEK/GOZLUK, örnek bölge, admin + formen |
| `V3…` / `V4…` | (ara seed / AI Core servis hesabı) |
| `V5__ai_core_servis_rolu.sql` | `AI_CORE_SERVIS` rolü; servis hesabı bu role taşınır |

## Dev/test hesapları (yalnızca yerel)

| Kullanıcı adı | Şifre | Rol |
|---|---|---|
| `admin` | `Admin123!` | ISG_YONETICI |
| `formen1` | `Formen123!` | FORMEN (bolge_id=1) |
| `ai_core_servis` | `AiCore123!` | AI_CORE_SERVIS (yalnızca `POST /api/ihlaller`) |

Üretimde şifreleri ve `JWT_SECRET` değerini mutlaka değiştirin.

## Fine-tune havuzu (MODÜL-6)

Yönetici bir ihlali reddettiğinde orijinal kanıt fotoğrafı
`uploads/finetune-havuz/{ihlalTipi}/` altına kopyalanır.

Mevcut `HATALI_TESPIT` kayıtlarını geriye dönük senkronize etmek için
(yönetici JWT ile):

```powershell
# repo kökünden, backend ayaktayken
./scripts/export-finetune-havuz.ps1
```
