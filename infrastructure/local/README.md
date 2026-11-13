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

Por padrão o worker usa o runtime *fake* (nada é executado). Para abrir os laboratórios de verdade no navegador:

```powershell
# na raiz do repositório (PowerShell)
docker compose -f infrastructure/local/docker-compose.yml -f infrastructure/local/docker-compose.docker-runtime.yml up --build -d
.\scripts\lab-local.ps1     # constrói as imagens do LAB-000 e do LAB-001 e registra as releases
```

Releases são imutáveis: se uma versão já foi publicada no banco local com outro conteúdo, o script avisa
(409) e segue para o próximo laboratório, mantendo a versão existente. Para publicar o conteúdo novo, suba a
versão no manifesto; recriar o banco (`down -v`) também resolve, mas **apaga** sessões e progresso locais.

Depois abra **http://127.0.0.1:8000** (use `127.0.0.1`, não `localhost`), entre com um usuário de teste
(ex.: `aluno1`), abra o LAB-000 e clique em **Iniciar laboratório**. Em alguns segundos aparecem:
etapas à esquerda e, à direita, as abas **Aplicação**, **Código**, **Terminal** e **Validação** (histórico
das validações). O botão **Código + Aplicação** mostra editor e aplicação lado a lado. Trocar de aba não
derruba o terminal. Edite `index.html`, salve com Ctrl+S e clique em **recarregar** para ver a mudança.
As dicas abrem em uma janela pelo botão **Dicas** ao lado de **Validar**. Arraste a divisa entre as
etapas e as abas para alargar o painel de explicação (duplo clique volta ao tamanho padrão).

Roteiro das etapas do LAB-000 0.2.1 (ADR-010):

1. **Explorar o ambiente**: descubra no terminal com qual usuário os comandos rodam (`whoami`), digite a
   resposta e clique em **Validar**. Respostas erradas mostram o critério que falhou. As tentativas são
   livres. A 1ª dica de cada etapa é grátis, a 2ª custa 1 ponto e a 3ª custa 2, com desconto total de
   no máximo 10% (ADR-013).
2. **Alterar a aplicação**: edite `index.html` para exibir "Olá, CECyber", salve e clique em **Validar**.
   O worker copia o workspace, sobe uma cópia isolada da aplicação e a testa de fora; leva alguns segundos.
   Ao concluir, a pontuação chega a 100/100 e aparece "Laboratório concluído".

Roteiro do **LAB-001 SQL Injection** (Clínica VidaPlena, dados fictícios, cerca de 40 min). As etapas
explicam cada passo; as respostas abaixo servem só para conferência:

1. **Conhecer a aplicação**: siga a busca do controller até o repositório. Resposta: `buscar_por_nome`.
2. **Provocar um erro**: busque por `'` e leia `tail -n 20 /tmp/app.log` no terminal. Resposta:
   `OperationalError`.
3. **Medir a consulta**: `' ORDER BY 5 --` dá erro e `' ORDER BY 4 --` funciona. Resposta: `4`.
4. **Extrair dados sensíveis**: `' UNION SELECT 1, chave, valor, '' FROM configuracoes --`. Resposta:
   o token `VP-INT-...` exibido.
5. **Corrigir**: em `repositories/medico_repository.py`, troque a f-string por `LIKE ?` com o valor em
   tupla, salve (a aplicação recarrega sozinha) e clique em **Validar**. O worker testa uma cópia isolada
   com buscas legítimas e ataques.

O LAB-001 contém vulnerabilidade **intencional**: ele roda só na rede interna da sessão, acessível pelo
gateway em 127.0.0.1. Não exponha em rede compartilhada.

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

### Prazo e sessões paradas (ADR-011/014)

Cada sessão tem o prazo do laboratório (ex.: 45 min no LAB-001) e pode ser renovada perto do fim. Sessões sem
atividade (cliques e teclas no portal, editor, terminal ou aplicação) são encerradas após 15 minutos, com aviso
3 minutos antes; o progresso fica salvo. Para testar com um limite curto:

```powershell
$env:SESSION_IDLE_MINUTES = "4"
docker compose -f infrastructure/local/docker-compose.yml -f infrastructure/local/docker-compose.docker-runtime.yml up -d
```

## Logs, parada e limpeza

```powershell
docker compose -f infrastructure/local/docker-compose.yml logs -f worker   # logs JSON
docker compose -f infrastructure/local/docker-compose.yml down             # para (mantém dados)
docker compose -f infrastructure/local/docker-compose.yml down -v          # para e APAGA o banco local
```

Alternativa sem Docker (Linux/macOS): `scripts/dev-db.sh start` + `scripts/demo-slice.sh`.
