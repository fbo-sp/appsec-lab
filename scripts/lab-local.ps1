# Constrói a imagem LOCAL do LAB-000 e registra a release apontando para o ID local da imagem.
# Uso (PowerShell, na raiz do repositório):  .\scripts\lab-local.ps1
# Somente para o runtime Docker local (ADR-008).
param([string]$Api = "http://127.0.0.1:8000")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Lab = Join-Path $Root "laboratories\LAB-000-hello-benign"
docker build -q -t cecyber-labs/base-python:local (Join-Path $Root "laboratories\_base\python") | Out-Null
if ($LASTEXITCODE -ne 0) { throw "docker build da base falhou" }
docker build -q -t cecyber-labs/lab-000-hello:local (Join-Path $Lab "runtime") | Out-Null
if ($LASTEXITCODE -ne 0) { throw "docker build falhou" }
$Id = (docker image inspect --format "{{.Id}}" cecyber-labs/lab-000-hello:local).Trim()
Write-Host "imagem local: $Id"
$Manifest = Get-Content -Raw -Encoding UTF8 (Join-Path $Lab "manifest.yaml")
$Manifest = [regex]::Replace($Manifest, "(?m)^(    image: ).*@sha256:[0-9a-f]{64}", "`${1}local/labs/lab-000-hello@$Id")
$Headers = @{ "X-Dev-User" = "admin"; "X-Dev-Roles" = "admin" }
try {
  $r = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$Api/api/v1/admin/lab-releases" `
    -Headers $Headers -ContentType "application/yaml" -Body ([Text.Encoding]::UTF8.GetBytes($Manifest))
  Write-Host "LAB-000 registrado ($($r.StatusCode))"
} catch {
  $code = $_.Exception.Response.StatusCode.value__
  if ($code -eq 409) {
    Write-Host "A release LAB-000@0.2.0 já existe com outra imagem. Recrie o banco local:"
    Write-Host "  docker compose -f infrastructure/local/docker-compose.yml down -v"
  }
  throw
}
