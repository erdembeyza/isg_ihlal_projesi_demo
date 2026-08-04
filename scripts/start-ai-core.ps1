# Guvenlik kamerasi / canli AI Core baslaticisi.
# Backend ayakta olmali. Kamera URL'si ai-core\.env icinde VIDEO_SOURCE.
param(
    [string]$Source = "",
    [string]$Cameras = "",
    [switch]$Loop,
    [switch]$Show,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$repoKok = Split-Path -Parent $PSScriptRoot
$aiCore = Join-Path $repoKok "ai-core"
$python = Join-Path $aiCore "venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "AI Core venv yok. Once: cd ai-core; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

if (-not (Test-Path (Join-Path $aiCore ".env"))) {
    Copy-Item (Join-Path $aiCore ".env.example") (Join-Path $aiCore ".env")
    Write-Host ".env olusturuldu (.env.example'dan). VIDEO_SOURCE'u kamera RTSP adresinizle duzenleyin." -ForegroundColor Yellow
}

$argsList = @("-m", "src.main")
if ($Cameras) { $argsList += @("--cameras", $Cameras) }
elseif ($Source) { $argsList += @("--source", $Source) }
if ($Loop) { $argsList += "--loop" }
if ($Show) { $argsList += "--show" }
if ($DryRun) { $argsList += "--dry-run" }

Write-Host "AI Core baslatiliyor (Ctrl+C ile durdurun)..." -ForegroundColor Cyan
Write-Host ("python " + ($argsList -join " ")) -ForegroundColor DarkGray
Set-Location $aiCore
& $python @argsList
