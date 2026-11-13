# Constrói as imagens LOCAIS dos laboratórios e registra cada release apontando para o ID local da imagem.
# Uso (PowerShell, na raiz do repositório):  .\scripts\lab-local.ps1
# Somente para o runtime Docker local (ADR-008). LAB-001 contém vulnerabilidade INTENCIONAL:
# roda só na rede interna da sessão, nunca exposto.
param([string]$Api = "http://127.0.0.1:8000")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Labs = @("LAB-000-hello-benign", "LAB-001-sqli-clinica")
docker build -q -t cecyber-labs/base-python:local (Join-Path $Root "laboratories\_base\python") | Out-Null
if ($LASTEXITCODE -ne 0) { throw "docker build da base falhou" }
$Headers = @{ "X-Dev-User" = "admin"; "X-Dev-Roles" = "admin" }
foreach ($Dir in $Labs) {
  $Lab = Join-Path $Root "laboratories\$Dir"
  $Manifest = Get-Content -Raw -Encoding UTF8 (Join-Path $Lab "manifest.yaml")
  $Name = [regex]::Match($Manifest, "(?m)^    image: registry\.local/labs/([a-z0-9-]+)@sha256:").Groups[1].Value
  $LabId = [regex]::Match($Manifest, "(?m)^  id: (LAB-[0-9]{3})\s*$").Groups[1].Value
  $Version = [regex]::Match($Manifest, "(?m)^  version: ([0-9][^\s]*)\s*$").Groups[1].Value
  docker build -q -t "cecyber-labs/${Name}:local" (Join-Path $Lab "runtime") | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker build de $LabId falhou" }
  $Id = (docker image inspect --format "{{.Id}}" "cecyber-labs/${Name}:local").Trim()
  Write-Host "${LabId}: imagem local $Id"
  $Body = [regex]::Replace($Manifest, "(?m)^(    image: ).*@sha256:[0-9a-f]{64}", "`${1}local/labs/$Name@$Id")
  try {
    $r = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$Api/api/v1/admin/lab-releases" `
      -Headers $Headers -ContentType "application/yaml" -Body ([Text.Encoding]::UTF8.GetBytes($Body))
    Write-Host "$LabId registrado ($($r.StatusCode))"
  } catch {
    $code = $_.Exception.Response.StatusCode.value__
    if ($code -eq 409) {
      Write-Host "A release $LabId@$Version já existe com outra imagem. Recrie o banco local:"
      Write-Host "  docker compose -f infrastructure/local/docker-compose.yml down -v"
    }
    throw
  }
}
