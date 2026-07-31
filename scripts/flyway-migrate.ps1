<#
.SYNOPSIS
    Flyway migration'larini (backend/src/main/resources/db/migration) standalone
    Flyway Docker imaji ile isg_postgres konteynerine uygular.

.DESCRIPTION
    Faz 2'de Spring Boot backend projesi olusturulup Flyway bagimliligi eklendiginde
    migration'lar uygulama ayaga kalkarken otomatik calisacaktir. Bu script, backend
    projesi henuz yokken (Faz 1) veya backend disinda manuel migration/dogrulama
    yapmak icin kullanilir.

.PARAMETER Command
    Flyway komutu: migrate | info | validate | clean (varsayilan: migrate)

.EXAMPLE
    ./scripts/flyway-migrate.ps1
    ./scripts/flyway-migrate.ps1 -Command info
#>
param(
    [ValidateSet('migrate', 'info', 'validate', 'clean')]
    [string]$Command = 'migrate'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$migrationPath = Join-Path $repoRoot 'backend\src\main\resources\db\migration'

if (-not (Test-Path $migrationPath)) {
    throw "Migration klasoru bulunamadi: $migrationPath"
}

docker run --rm --network isg_ihlal_projesi_default `
    -v "${migrationPath}:/flyway/sql" `
    flyway/flyway:10-alpine `
    -url=jdbc:postgresql://postgres:5432/isg_ihlal_db `
    -user=isg_admin -password=isg_admin_pw `
    -connectRetries=5 `
    $Command
