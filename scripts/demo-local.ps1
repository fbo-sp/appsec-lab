# Demonstração da 1ª fatia contra o ambiente Docker Compose local (Windows / PowerShell 5.1+).
# Pré-requisito: docker compose -f infrastructure/local/docker-compose.yml up --build -d
# Uso:  powershell -ExecutionPolicy Bypass -File scripts\demo-local.ps1
$ErrorActionPreference = "Stop"
$Api = if ($env:APPSEC_API) { $env:APPSEC_API } else { "http://127.0.0.1:8000" }
$Root = Split-Path -Parent $PSScriptRoot
$Admin = @{ "X-Dev-User" = "admin-demo"; "X-Dev-Roles" = "admin" }
$Aluno = @{ "X-Dev-User" = "aluno-demo"; "X-Dev-Roles" = "student" }

function Get-SessionStatus([string]$Id, [hashtable]$Headers) {
    (Invoke-RestMethod -Uri "$Api/api/v1/sessions/$Id" -Headers $Headers).status
}
function Wait-Status([string]$Id, [string]$Expected) {
    for ($i = 0; $i -lt 40; $i++) {
        $s = Get-SessionStatus $Id $Aluno
        if ($s -eq $Expected) { return $s }
        Start-Sleep -Milliseconds 500
    }
    return $s
}

Write-Host "== 0. Saude da API"
Invoke-RestMethod -Uri "$Api/healthz" | ConvertTo-Json -Compress

Write-Host "== 1. Registrar LAB-000 (benigno, sem vulnerabilidade)"
$manifest = [System.IO.File]::ReadAllText((Join-Path $Root "laboratories\LAB-000-hello-benign\manifest.yaml"))
$rel = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$Api/api/v1/admin/lab-releases" -Headers $Admin `
    -ContentType "application/yaml; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($manifest))
Write-Host "HTTP $($rel.StatusCode) (201 = publicado, 200 = ja existia)"

Write-Host "== 2. Criar sessao com Idempotency-Key"
$key = "demo-" + [guid]::NewGuid().ToString("N")
$body = '{"labId":"LAB-000","version":"0.1.0","variantId":"python-http"}'
$h = $Aluno.Clone(); $h["Idempotency-Key"] = $key
$s1 = Invoke-RestMethod -Method Post -Uri "$Api/api/v1/sessions" -Headers $h -ContentType "application/json" -Body $body
Write-Host "sessionId=$($s1.sessionId) status=$($s1.status)"

Write-Host "== 3. Repetir com a mesma chave (mesma sessao esperada)"
$s2 = Invoke-RestMethod -Method Post -Uri "$Api/api/v1/sessions" -Headers $h -ContentType "application/json" -Body $body
Write-Host "sessionId=$($s2.sessionId) iguais=$($s1.sessionId -eq $s2.sessionId)"

Write-Host "== 4. Aguardar READY"
Write-Host "status=$(Wait-Status $s1.sessionId 'READY')"

Write-Host "== 5. Outro aluno nao enxerga a sessao (404 esperado)"
try {
    Invoke-RestMethod -Uri "$Api/api/v1/sessions/$($s1.sessionId)" -Headers @{ "X-Dev-User" = "outro-aluno" } | Out-Null
    Write-Host "FALHA: sessao visivel para outro usuario"
} catch { Write-Host "HTTP $([int]$_.Exception.Response.StatusCode)" }

Write-Host "== 6. Encerrar sessao"
$t = Invoke-RestMethod -Method Delete -Uri "$Api/api/v1/sessions/$($s1.sessionId)" -Headers $Aluno
Write-Host "status=$($t.status)"
Write-Host "status=$(Wait-Status $s1.sessionId 'TERMINATED')"
Write-Host "`nLogs estruturados: docker compose -f infrastructure/local/docker-compose.yml logs worker"
Write-Host "API interativa (Swagger): $Api/api/docs"
