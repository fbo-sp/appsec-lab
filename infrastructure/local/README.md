# Ambiente local (Docker Desktop)

Executa somente componentes **confiáveis** da 1ª fatia: PostgreSQL, migração, API e worker.
O runtime de laboratórios é o `FakeRuntimeAdapter` (não executa contêineres de aluno). Docker Compose
**não** é fronteira de isolamento para código hostil (docs/07, ADR-002).

## Subir

```powershell
# na raiz do repositório
docker compose -f infrastructure/local/docker-compose.yml up --build -d
docker compose -f infrastructure/local/docker-compose.yml ps        # api deve ficar "healthy"
```

- API: http://127.0.0.1:8000 · Swagger: http://127.0.0.1:8000/api/docs
- PostgreSQL: 127.0.0.1:5432 (usuário `appsec`, senha local `local-dev-only` ou `POSTGRES_PASSWORD`)
- Autenticação de desenvolvimento por cabeçalho: `X-Dev-User: <id>` e `X-Dev-Roles: student|admin`

## Demonstração

```powershell
powershell -ExecutionPolicy Bypass -File scripts\demo-local.ps1
```

Registra o LAB-000, cria a sessão (com replay idempotente), aguarda `READY`, verifica que outro usuário
recebe 404 e encerra até `TERMINATED`.

## Teste visual: laboratório no navegador (runtime Docker local — ADR-008/009)

Por padrão o worker usa o runtime *fake* (nada é executado). Para abrir o LAB-000 de verdade no navegador:

```powershell
# na raiz do repositório (PowerShell)
docker compose -f infrastructure/local/docker-compose.yml down -v      # se já subiu antes: recomeça limpo
docker compose -f infrastructure/local/docker-compose.yml -f infrastructure/local/docker-compose.docker-runtime.yml up --build -d
.\scripts\lab-local.ps1     # constrói as imagens do LAB-000 e registra a release
```

Depois abra **http://127.0.0.1:8000** (use `127.0.0.1`, não `localhost`), entre com um usuário de teste
(ex.: `aluno1`), abra o LAB-000 e clique em **Iniciar laboratório**. Em alguns segundos aparecem:
etapas à esquerda e, à direita, as abas **Aplicação**, **Código**, **Terminal** e **Validação** (histórico
das validações). O botão **Código + Aplicação** mostra editor e aplicação lado a lado. Trocar de aba não
derruba o terminal. Edite `index.html`, salve com Ctrl+S e clique em **recarregar** para ver a mudança.
As dicas abrem em uma janela pelo botão **Dicas** ao lado de **Validar**.

Roteiro das etapas do LAB-000 0.2.1 (ADR-010):

1. **Explorar o ambiente**: descubra no terminal com qual usuário os comandos rodam (`whoami`), digite a
   resposta e clique em **Validar**. Respostas erradas mostram o critério que falhou. As tentativas são
   livres e as dicas não descontam pontos.
2. **Alterar a aplicação**: edite `index.html` para exibir "Olá, CECyber", salve e clique em **Validar**.
   O worker copia o workspace, sobe uma cópia isolada da aplicação e a testa de fora; leva alguns segundos.
   Ao concluir, a pontuação chega a 100/100 e aparece "Laboratório concluído".

O progresso fica na tentativa do usuário: encerrar e iniciar de novo retoma as etapas já concluídas. Para
recomeçar do zero, use outro usuário de teste.

Portas (todas só em 127.0.0.1): 8000 portal + API, 8001 workspace (editor/terminal), 8002 aplicação do lab.

- O socket Docker é montado **somente no worker**; laboratórios rodam em rede interna própria, sem
  portas no host, como usuário não-root e com raiz somente leitura. O gateway é o único outro participante
  dessa rede e exige ticket de uso único emitido ao dono da sessão.
- Uso exclusivo na máquina do desenvolvedor. **Não** é isolamento para código hostil nem configuração de
  piloto/produção. Não use em máquina compartilhada (acesso ao socket equivale a root).
- Contêineres de sessão: `docker ps --filter label=io.cecyber.appsec-labs.platform=appsec-labs-local`.
- Se a sessão ficar em "Preparando ambiente" e falhar, veja `docker compose ... logs worker`.

## Logs, parada e limpeza

```powershell
docker compose -f infrastructure/local/docker-compose.yml logs -f worker   # logs JSON
docker compose -f infrastructure/local/docker-compose.yml down             # para (mantém dados)
docker compose -f infrastructure/local/docker-compose.yml down -v          # para e APAGA o banco local
```

Alternativa sem Docker (Linux/macOS): `scripts/dev-db.sh start` + `scripts/demo-slice.sh`.
