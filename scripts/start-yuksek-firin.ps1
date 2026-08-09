# Yuksek Firin: A ve B bolgesi kameralarini ayni anda baslatir (video = canli simulasyon).
# Backend ayakta olmali. Durdurmak: Ctrl+C veya pencerede 'q'.
param(
    [switch]$DryRun,
    [switch]$NoShow
)

$ErrorActionPreference = "Stop"
$repoKok = Split-Path -Parent $PSScriptRoot
$aiCore = Join-Path $repoKok "ai-core"
$python = Join-Path $aiCore "venv\Scripts\python.exe"
$cameras = "cameras.yuksek-firin.json"
$videoA = Join-Path $aiCore "test_videos\a_bolgesi.mp4"
$videoB = Join-Path $aiCore "test_videos\b_bolgesi.mp4"

if (-not (Test-Path $python)) {
    throw "AI Core venv yok. Once: cd ai-core; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

if (-not (Test-Path (Join-Path $aiCore ".env"))) {
    Copy-Item (Join-Path $aiCore ".env.example") (Join-Path $aiCore ".env")
    Write-Host ".env olusturuldu (.env.example'dan)." -ForegroundColor Yellow
}

$testVideos = Join-Path $aiCore "test_videos"
if (-not (Test-Path $testVideos)) {
    New-Item -ItemType Directory -Path $testVideos | Out-Null
}

foreach ($pair in @(
    @{ Yol = $videoA; Ad = "a_bolgesi.mp4" },
    @{ Yol = $videoB; Ad = "b_bolgesi.mp4" }
)) {
    if (-not (Test-Path $pair.Yol)) {
        Write-Host "Eksik video uretiliyor: $($pair.Ad)" -ForegroundColor Yellow
        & $python (Join-Path $aiCore "tools\test_video_uret.py") --cikti $pair.Yol --kare-sayisi 60
        if ($LASTEXITCODE -ne 0) {
            throw "Video uretilemedi: $($pair.Ad). Gercek kayitlari test_videos\ altina koyabilirsiniz."
        }
    }
}

$argsList = @("-m", "src.main", "--cameras", $cameras)
if (-not $NoShow) { $argsList += "--show" }
if ($DryRun) { $argsList += "--dry-run" }

Write-Host "Yuksek Firin A + B kameralari ayni anda baslatiliyor..." -ForegroundColor Cyan
Write-Host ("python " + ($argsList -join " ")) -ForegroundColor DarkGray
Set-Location $aiCore
& $python @argsList
