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

## Runtime Docker local (laboratórios como contêineres reais — ADR-008)

Por padrão o worker usa o runtime *fake* (nada é executado). Para executar o LAB-000 de verdade:

```powershell
docker compose -f infrastructure/local/docker-compose.yml -f infrastructure/local/docker-compose.docker-runtime.yml up --build -d
.\scripts\lab-local.ps1     # constrói a imagem do LAB-000 e registra a release com o ID local
```

- O socket Docker é montado **somente no worker**; laboratórios rodam em rede interna própria, sem
  portas no host, como usuário não-root e com raiz somente leitura.
- Uso exclusivo na máquina do desenvolvedor. **Não** é isolamento para código hostil nem configuração de
  piloto/produção. Não use em máquina compartilhada (acesso ao socket equivale a root).
- Contêineres de sessão: `docker ps --filter label=io.cecyber.appsec-labs.platform=appsec-labs-local`.
- Ainda não há gateway: a aplicação do laboratório não é acessível pelo navegador nesta etapa.

## Logs, parada e limpeza

```powershell
docker compose -f infrastructure/local/docker-compose.yml logs -f worker   # logs JSON
docker compose -f infrastructure/local/docker-compose.yml down             # para (mantém dados)
docker compose -f infrastructure/local/docker-compose.yml down -v          # para e APAGA o banco local
```

Alternativa sem Docker (Linux/macOS): `scripts/dev-db.sh start` + `scripts/demo-slice.sh`.
