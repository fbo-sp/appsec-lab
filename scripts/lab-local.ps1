# Constrói as imagens LOCAIS dos laboratórios e registra cada release apontando para o ID local da imagem.
# Uso (PowerShell, na raiz do repositório):  .\scripts\lab-local.ps1
# Somente para o runtime Docker local (ADR-008). LAB-001 a LAB-004 contêm vulnerabilidades INTENCIONAIS:
# rodam só na rede interna da sessão, nunca expostos.
param([string]$Api = "http://127.0.0.1:8000")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Labs = @("LAB-000-hello-benign", "LAB-001-sqli-clinica", "LAB-002-idor-banco", "LAB-003-jwt-cartoes",
  "LAB-004-cmdi-industria")
docker build -q -t cecyber-labs/base-python:local (Join-Path $Root "laboratories\_base\python") | Out-Null
if ($LASTEXITCODE -ne 0) { throw "docker build da base falhou" }
# Base Node.js (LAB-003): parte da base Python, que traz o agente de workspace.
docker build -q -t cecyber-labs/base-node:local (Join-Path $Root "laboratories\_base\node") | Out-Null
if ($LASTEXITCODE -ne 0) { throw "docker build da base Node falhou" }
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
      # Release imutável já publicada com outro conteúdo/imagem: avisa e segue para o próximo laboratório.
      Write-Warning "$LabId@$Version já está publicada com conteúdo diferente (409); mantida a versão existente."
      Write-Warning "  Para publicar a nova, suba a versão no manifesto (ou recrie o banco local, apagando os dados)."
      continue
    }
    throw
  }
}
