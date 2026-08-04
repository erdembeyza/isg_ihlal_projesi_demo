# Toplu ihlal kaydi temizligi.
# Dosyasi silinmis (yetim) kayitlari veya tarih araligindaki / tum kayitlari kaldirir.
#
# Ornekler:
#   .\scripts\temizle-ihlaller.ps1 -Yetimler -DryRun          # ne silinecek, sadece goster
#   .\scripts\temizle-ihlaller.ps1 -Yetimler                  # dosyasi olmayan kayitlari sil
#   .\scripts\temizle-ihlaller.ps1 -Baslangic "2026-08-01" -Bitis "2026-08-04" -DryRun
#   .\scripts\temizle-ihlaller.ps1 -TumunuSil -DryRun       # tum kayitlar (dikkat!)
#
param(
    [switch]$Yetimler,          # orijinal_foto_yolu dosyasi diskte yoksa sil
    [switch]$TumunuSil,         # tum ihlaller tablosunu bosalt
    [string]$Baslangic,         # ornek: 2026-08-01
    [string]$Bitis,             # ornek: 2026-08-04 (dahil, gun sonu)
    [switch]$DryRun,            # silme yapma, sadece listele
    [switch]$Onayla,            # onay sormadan sil (otomasyon icin)
    [string]$UploadDir = "backend\uploads",
    [string]$DbContainer = "isg_postgres",
    [string]$DbUser = "isg_admin",
    [string]$DbName = "isg_ihlal_db"
)

$ErrorActionPreference = "Stop"

function Invoke-Psql {
    param([string]$Sql)
    $out = docker exec $DbContainer psql -U $DbUser -d $DbName -t -A -F "|" -c $Sql 2>&1
    if ($LASTEXITCODE -ne 0) { throw "psql hatasi: $out" }
    return $out
}

function Get-IhlalKayitlari {
    $where = @()
    if ($Baslangic) { $where += "tespit_zamani >= '$Baslangic 00:00:00'" }
    if ($Bitis)     { $where += "tespit_zamani <= '$Bitis 23:59:59'" }

    $sql = "SELECT id, orijinal_foto_yolu, tespit_zamani, durum FROM ihlaller"
    if ($where.Count -gt 0) { $sql += " WHERE " + ($where -join " AND ") }
    $sql += " ORDER BY id"

    $satirlar = @(Invoke-Psql -Sql $sql | Where-Object { $_.Trim() -ne "" })
    foreach ($satir in $satirlar) {
        $p = $satir -split "\|", 4
        [PSCustomObject]@{
            Id       = [long]$p[0]
            FotoYolu = $p[1]
            Tespit   = $p[2]
            Durum    = $p[3]
        }
    }
}

function Test-FotoVar {
    param([string]$FotoYolu)
    if (-not $FotoYolu) { return $false }
    $rel = $FotoYolu -replace "^/uploads/", ""
    $disk = Join-Path (Resolve-Path $UploadDir) ($rel -replace "/", [IO.Path]::DirectorySeparatorChar)
    return Test-Path -LiteralPath $disk
}

function Remove-IhlalKayitlari {
    param([long[]]$Ids)
    if ($Ids.Count -eq 0) { return 0 }

    $idList = ($Ids | Sort-Object -Unique) -join ","
    $logSql = "DELETE FROM islem_loglari WHERE ilgili_ihlal_id IN ($idList);"
    $ihlalSql = "DELETE FROM ihlaller WHERE id IN ($idList);"

    Invoke-Psql -Sql "BEGIN; $logSql $ihlalSql COMMIT;" | Out-Null
    return $Ids.Count
}

# --- Mod secimi ---
if (-not $Yetimler -and -not $TumunuSil -and -not $Baslangic -and -not $Bitis) {
    Write-Host @"
Kullanim:
  -Yetimler     Dosyasi diskte olmayan kayitlari hedefler (sizin durumunuz)
  -TumunuSil    Tum ihlal kayitlarini siler
  -Baslangic    Tarih filtresi baslangici (YYYY-MM-DD)
  -Bitis        Tarih filtresi bitisi (YYYY-MM-DD)
  -DryRun       Silmeden once listele
  -Onayla       Onay sormadan uygula

Ornek (once dry-run):
  .\scripts\temizle-ihlaller.ps1 -Yetimler -DryRun
  .\scripts\temizle-ihlaller.ps1 -Yetimler
"@ -ForegroundColor Yellow
    exit 1
}

Write-Host "PostgreSQL konteyneri: $DbContainer" -ForegroundColor Cyan
$containerDurum = docker ps --filter "name=$DbContainer" --format "{{.Names}}" 2>&1
if (-not $containerDurum) {
    throw "Docker konteyneri '$DbContainer' calismiyor. Once: docker compose up -d postgres"
}

$uploadAbs = Resolve-Path $UploadDir -ErrorAction SilentlyContinue
if (-not $uploadAbs) {
    throw "Upload klasoru bulunamadi: $UploadDir"
}

$kayitlar = @(Get-IhlalKayitlari)
Write-Host "Veritabaninda $($kayitlar.Count) kayit bulundu." -ForegroundColor Cyan

$silinecek = @()

if ($TumunuSil) {
    $silinecek = $kayitlar
    Write-Host "Mod: TUM kayitlar silinecek." -ForegroundColor Red
}
elseif ($Yetimler) {
    foreach ($k in $kayitlar) {
        if (-not (Test-FotoVar -FotoYolu $k.FotoYolu)) {
            $silinecek += $k
        }
    }
    Write-Host "Mod: Dosyasi olmayan (yetim) kayitlar. Bulunan: $($silinecek.Count)" -ForegroundColor Yellow
}
else {
    $silinecek = $kayitlar
    $filtre = @()
    if ($Baslangic) { $filtre += "baslangic=$Baslangic" }
    if ($Bitis)     { $filtre += "bitis=$Bitis" }
    Write-Host "Mod: Tarih filtresi ($($filtre -join ', ')). Eslesen: $($silinecek.Count)" -ForegroundColor Yellow
}

if ($silinecek.Count -eq 0) {
    Write-Host "Silinecek kayit yok." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Silinecek kayitlar (ilk 20):" -ForegroundColor Cyan
$silinecek | Select-Object -First 20 | ForEach-Object {
    Write-Host ("  id={0,-6} {1,-20} {2}" -f $_.Id, $_.Durum, $_.FotoYolu)
}
if ($silinecek.Count -gt 20) {
    Write-Host "  ... ve $($silinecek.Count - 20) kayit daha"
}

if ($DryRun) {
    Write-Host ""
    Write-Host "DRY-RUN: $($silinecek.Count) kayit silinmedi. Gercek silme icin -DryRun kaldirin." -ForegroundColor Green
    exit 0
}

if (-not $Onayla) {
    Write-Host ""
    $cevap = Read-Host "$($silinecek.Count) kayit silinsin mi? (evet/hayir)"
    if ($cevap -notmatch "^(e|evet|y|yes)$") {
        Write-Host "Iptal edildi." -ForegroundColor Yellow
        exit 0
    }
}

$ids = @($silinecek | ForEach-Object { $_.Id })
$batchSize = 500
$silinen = 0

for ($i = 0; $i -lt $ids.Count; $i += $batchSize) {
    $batch = $ids[$i..([Math]::Min($i + $batchSize - 1, $ids.Count - 1))]
    $silinen += Remove-IhlalKayitlari -Ids $batch
    Write-Host "Silindi: $silinen / $($ids.Count)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Tamamlandi. Toplam $silinen kayit silindi." -ForegroundColor Green
Write-Host "Web sayfasini yenileyin; kirik fotolar kaybolmus olmali." -ForegroundColor Green
