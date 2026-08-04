# Egitim sonrasi best.pt dosyasini uretim modeli konumuna kopyalar.
param(
    [string]$Kaynak = "runs\detect\isg_guncellenmis_model\weights\best.pt"
)

$ErrorActionPreference = "Stop"
$AiCore = Split-Path $PSScriptRoot -Parent
$KaynakYol = Join-Path $AiCore $Kaynak
$HedefYol = Join-Path $AiCore "models\ppe_yolov8n.pt"

if (-not (Test-Path $KaynakYol)) {
    throw "Egitilmis model bulunamadi: $KaynakYol`nOnce python training\egitim_scripti.py calistirin."
}

$yedek = Join-Path $AiCore "models\ppe_yolov8n.pt.yedek"
if (Test-Path $HedefYol) {
    Copy-Item $HedefYol $yedek -Force
    Write-Host "Eski model yedeklendi: $yedek" -ForegroundColor Yellow
}

Copy-Item $KaynakYol $HedefYol -Force
Write-Host "Uretim modeli guncellendi: $HedefYol" -ForegroundColor Green
