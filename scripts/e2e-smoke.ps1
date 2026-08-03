# Uctan uca duman testi (Faz 8) - tasarim_mimari.md MODUL-1..6
param(
    [string]$BackendBase = "http://localhost:8080",
    [string]$Video = "ai-core\test_videos\demo.mp4",
    [string]$AiCoreDir = "ai-core"
)

$ErrorActionPreference = "Stop"

function Write-Adim([string]$msg) {
    Write-Host ""
    Write-Host "=== $msg ===" -ForegroundColor Cyan
}

Write-Adim "1 Backend saglik kontrolu"
try {
    $ping = Invoke-RestMethod -Uri "$BackendBase/api/auth/login" -Method POST -ContentType "application/json" `
        -Body '{"kullaniciAdi":"admin","sifre":"Admin123!"}' -TimeoutSec 10
    if (-not $ping.token) { throw "Login yaniti token icermiyor" }
    $adminToken = $ping.token
    Write-Host "OK admin girisi basarili rol=$($ping.rol)"
} catch {
    Write-Host "HATA: Backend $BackendBase yanit vermiyor. Once backend'i baslatin." -ForegroundColor Red
    throw
}

Write-Adim "2 AI Core servis hesabi V4 ile login"
$aiLogin = Invoke-RestMethod -Uri "$BackendBase/api/auth/login" -Method POST -ContentType "application/json" `
    -Body '{"kullaniciAdi":"ai_core_servis","sifre":"AiCore123!"}' -TimeoutSec 10
if (-not $aiLogin.token) { throw "ai_core_servis login basarisiz" }
Write-Host "OK ai_core_servis JWT alindi"

Write-Adim "3 Onceki ihlal sayisi admin"
$headers = @{ Authorization = "Bearer $adminToken" }
# Measure-Object: PS 5.1'de tek/cok elemanli JSON dizilerinde .Count yaniltici olabiliyor
$oncekiSayi = @(Invoke-RestMethod -Uri "$BackendBase/api/ihlaller" -Headers $headers -TimeoutSec 15 | ForEach-Object { $_ }).Count
Write-Host "Mevcut ihlal kaydi: $oncekiSayi"

Write-Adim "4 AI Core gercek PPE modeli ile video POST"
$videoTam = (Resolve-Path $Video).Path
$python = Join-Path $AiCoreDir "venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "AI Core venv bulunamadi: $python" }
$model = Join-Path $AiCoreDir "models\ppe_yolov8n.pt"
if (-not (Test-Path $model)) {
    Write-Host "UYARI: $model yok - DEMO_MODU'na dusecek." -ForegroundColor Yellow
}

Push-Location $AiCoreDir
try {
    # Python logging stderr'e yazar; Stop tercihinde NativeCommandError olmamasi icin
    # gecici olarak Continue kullanilir, sonra exit code kontrol edilir.
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & .\venv\Scripts\python.exe -m src.main --source $videoTam
    $aiExit = $LASTEXITCODE
    $ErrorActionPreference = $prevEap
    if ($aiExit -ne 0) { throw "AI Core exit code: $aiExit" }
} finally {
    Pop-Location
}

Write-Adim "5 Yeni ihlaller admin GET"
$sonra = @(Invoke-RestMethod -Uri "$BackendBase/api/ihlaller" -Headers $headers -TimeoutSec 15 | ForEach-Object { $_ })
$sonraSayi = $sonra.Count
$eklenen = $sonraSayi - $oncekiSayi
Write-Host "Yeni kayit sayisi: $eklenen onceki=$oncekiSayi simdi=$sonraSayi"
if ($eklenen -lt 1) {
    Write-Host "UYARI: Yeni ihlal eklenmedi. Videoda NO-Hardhat/NO-Safety Vest yoksa normal olabilir." -ForegroundColor Yellow
} else {
    $son = $sonra | Sort-Object id -Descending | Select-Object -First 3
    foreach ($item in $son) {
        Write-Host ("  id={0} tip={1} bolge={2} durum={3} foto={4}" -f $item.id, $item.ihlalTipiAdi, $item.bolgeAdi, $item.durum, $item.fotoUrl)
    }
}

Write-Adim "6 Formen kapsami kendi bolgesi blurlu foto"
$formenLogin = Invoke-RestMethod -Uri "$BackendBase/api/auth/login" -Method POST -ContentType "application/json" `
    -Body '{"kullaniciAdi":"formen1","sifre":"Formen123!"}' -TimeoutSec 10
$formenHeaders = @{ Authorization = "Bearer $($formenLogin.token)" }
$formenListe = @(Invoke-RestMethod -Uri "$BackendBase/api/ihlaller" -Headers $formenHeaders -TimeoutSec 15 | ForEach-Object { $_ })
Write-Host "Formen ihlal sayisi: $($formenListe.Count) bolgeId=$($formenLogin.bolgeId)"
$orijinalSizan = @($formenListe | Where-Object { $_.fotoUrl -like "*orijinal*" })
if ($orijinalSizan.Count -gt 0) {
    throw "Formen yanitinda orijinal foto URL gorundu - KVKK hatasi"
}
Write-Host "OK formen yanitlarinda orijinal foto yolu yok"

Write-Adim "7 Istatistik ve reddet MODUL-2 / MODUL-6"
$istat = @(Invoke-RestMethod -Uri "$BackendBase/api/ihlaller/istatistik" -Headers $headers -TimeoutSec 15 | ForEach-Object { $_ })
Write-Host "Istatistik satir sayisi: $($istat.Count)"
foreach ($row in ($istat | Select-Object -First 5)) {
    Write-Host ("  {0} / {1}: adet={2} degisim={3}%" -f $row.bolgeAdi, $row.ihlalTipiAdi, $row.toplamAdet, $row.yuzdeDegisim)
}

$aktif = @($sonra | Where-Object { $_.durum -eq "AKTIF" } | Sort-Object id -Descending)
if ($aktif.Count -gt 0) {
    $redId = $aktif[0].id
    $red = Invoke-RestMethod -Uri "$BackendBase/api/ihlaller/$redId/reddet" -Method POST -Headers $headers `
        -ContentType "application/json" -Body '{"redNedeni":"Faz 8 e2e duman testi"}' -TimeoutSec 15
    if ($red.durum -ne "HATALI_TESPIT") { throw "Reddet sonrasi durum HATALI_TESPIT olmadi: $($red.durum)" }
    Write-Host "OK ihlal id=$redId HATALI_TESPIT olarak isaretlendi (MODUL-6)"
} else {
    Write-Host "UYARI: Reddet testi icin AKTIF kayit bulunamadi" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "E2E duman testi tamamlandi." -ForegroundColor Green
