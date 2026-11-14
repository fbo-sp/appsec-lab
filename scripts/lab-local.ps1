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
  # Cada release registrada fica presa a uma imagem com tag de versão (cecyber-labs/<nome>:<versão>).
  # Release é imutável: se essa tag já existe, ela é reaproveitada e NADA é reconstruído para essa versão.
  # Sem isso, reconstruir a base trocava o ID das imagens e as releases já registradas ficavam órfãs.
  $Pinned = "cecyber-labs/${Name}:$Version"
  # docker images -q devolve vazio quando a tag não existe; "image inspect" escreveria em stderr,
  # o que o PowerShell 5.1 trata como erro fatal com ErrorActionPreference=Stop.
  if (docker images -q $Pinned) {
    Write-Host "$LabId@${Version}: reaproveitando a imagem $Pinned"
  } else {
    docker build -q -t "cecyber-labs/${Name}:local" (Join-Path $Lab "runtime") | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "docker build de $LabId falhou" }
    docker tag "cecyber-labs/${Name}:local" $Pinned
    if ($LASTEXITCODE -ne 0) { throw "docker tag de $LabId falhou" }
  }
  $Id = (docker image inspect --format "{{.Id}}" $Pinned).Trim()
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
      Write-Warning "$LabId@$Version já está publicada com outra imagem ou conteúdo (409); mantida a versão existente."
      Write-Warning "  Se as sessões desse lab falharem com 'imagem não encontrada', a imagem registrada foi removida:"
      Write-Warning "  suba a versão no manifesto ou recrie o banco local (apaga os dados)."
      continue
    }
    throw
  }
}
