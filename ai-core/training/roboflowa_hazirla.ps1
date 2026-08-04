# Yeni gorselleri Roboflow'a yuklemeden once tek klasorde toplar.
# Kaynaklar: test_videos/, backend/uploads/finetune-havuz/
param(
    [string]$Cikti = "training\roboflow_yukleme"
)

$ErrorActionPreference = "Stop"
$AiCore = Split-Path $PSScriptRoot -Parent
$CiktiYol = Join-Path $AiCore $Cikti
New-Item -ItemType Directory -Force -Path $CiktiYol | Out-Null

$sayac = 0

function Kopyala-Gorsel {
    param([string]$Path, [string]$Prefix)
    if (-not (Test-Path $Path)) { return }
    Get-ChildItem -Path $Path -File -Include *.jpg,*.jpeg,*.png,*.webp -Recurse | ForEach-Object {
        $script:sayac++
        $hedef = Join-Path $CiktiYol ("{0}_{1:D3}{2}" -f $Prefix, $script:sayac, $_.Extension)
        Copy-Item $_.FullName $hedef
    }
}

$testVideos = Join-Path $AiCore "test_videos"
Kopyala-Gorsel -Path $testVideos -Prefix "test"

$finetune = Join-Path (Split-Path $AiCore -Parent) "backend\uploads\finetune-havuz"
Kopyala-Gorsel -Path $finetune -Prefix "havuz"

Write-Host "Toplam $sayac gorsel kopyalandi: $CiktiYol" -ForegroundColor Green
Write-Host ""
Write-Host "Sonraki adimlar:" -ForegroundColor Cyan
Write-Host "  1. https://roboflow.com adresinde yeni proje acin"
Write-Host "  2. Bu klasordeki gorselleri yukleyin"
Write-Host "  3. Sinif isimlerini mevcut modelle ayni yapin (python training\siniflari_goster.py)"
Write-Host "  4. Generate -> YOLOv8 -> Download zip"
Write-Host "  5. Zip'i training\yeni_veri_seti\ icine cikartin"
