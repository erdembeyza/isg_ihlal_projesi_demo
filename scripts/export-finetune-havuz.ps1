# MODUL-6: HATALI_TESPIT orijinal fotolarini fine-tune havuzuna senkronize eder.
# Backend ayakta olmali. Cikti: backend/uploads/finetune-havuz/{ihlalTipi}/
param(
    [string]$BackendBase = "http://localhost:8080",
    [string]$AdminUser = "admin",
    [string]$AdminPassword = "Admin123!"
)

$ErrorActionPreference = "Stop"

Write-Host "Yonetici girisi..." -ForegroundColor Cyan
$login = Invoke-RestMethod -Uri "$BackendBase/api/auth/login" -Method POST -ContentType "application/json" `
    -Body (@{ kullaniciAdi = $AdminUser; sifre = $AdminPassword } | ConvertTo-Json) -TimeoutSec 15

if (-not $login.token) { throw "Login basarisiz" }

$headers = @{ Authorization = "Bearer $($login.token)" }
Write-Host "Fine-tune havuzu senkronize ediliyor..." -ForegroundColor Cyan
$result = Invoke-RestMethod -Uri "$BackendBase/api/ihlaller/finetune-havuz/senkronize" `
    -Method POST -Headers $headers -TimeoutSec 60

Write-Host ("Toplam={0} Kopyalanan={1} Atlanan(kaynak yok)={2} Hata={3}" -f `
    $result.toplam, $result.kopyalanan, $result.atlanan, $result.hata)
Write-Host "Havuz klasoru: backend\uploads\finetune-havuz\" -ForegroundColor Green
