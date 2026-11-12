# ADR-008: Runtime Docker exclusivo para desenvolvimento e teste local

- **Status:** **Aprovado** pelo Product Owner em 2026-11-12 (escolha "Sim, adapter Docker local" e confirmação "está aprovado")
- **Data:** 2026-11-12
- **Contexto de origem:** pedido do PO de testar manualmente apenas com interface visual de um laboratório; `22` R-01/R-02; ADR-001/002 sem PoC; bloqueador "inventário on-prem"

## Contexto

O adapter fake (IMP-108) não executa nada, então não há aplicação para o gateway, editor, terminal ou preview exibirem. O runtime de produção (ADR-001) e o isolamento (ADR-002) dependem de PoC na infraestrutura on-premises, ainda indisponível. Sem um runtime executável, as fases de gateway (IMP-302), interface (IMP-303–305), validação (IMP-401–405) e LAB-001 (IMP-501) não podem ser testadas de ponta a ponta.

## Alternativas

| Alternativa | Prós | Contras |
|---|---|---|
| A. Esperar a PoC on-prem | Nenhum risco novo | Bloqueia toda a experiência visual por tempo indeterminado |
| **B. `DockerRuntimeAdapter` restrito a `APP_ENV=local\|test`** | Desbloqueia gateway/UI/validação; usa o Docker Desktop já disponível; implementa o mesmo `RuntimePort` | Docker não é fronteira adequada para código hostil; risco de ser confundido com solução de produção |
| C. Kubernetes local (kind/k3d) | Mais próximo de ADR-001 | Pré-julga ADR-001; mais pesado para o PO no Windows |

## Decisão

Alternativa **B**, com as restrições:

1. **Somente local/test.** `Settings.check` recusa `RUNTIME_ADAPTER=docker` (e qualquer adapter) fora de `APP_ENV=local|test`. Não é opção de piloto nem de produção; não substitui ADR-001/002.
2. **Socket Docker só no worker** (plano de controle confiável), via override `infrastructure/local/docker-compose.docker-runtime.yml`. Nunca em contêiner de laboratório, API ou gateway. Acesso ao socket equivale a root na máquina: não usar em máquina compartilhada.
3. **Controles por sessão** (verificados em `tests/test_docker_local_isolation.py`):
   - rede `internal` exclusiva por sessão, sem masquerade; nenhuma porta publicada no host;
   - imagem obrigatoriamente com `USER` não-root; `cap_drop=ALL`; `no-new-privileges`; não privilegiado;
   - raiz somente leitura; `/tmp` em tmpfs `noexec`; workspace em volume nomeado da sessão;
   - limites de CPU, memória (sem swap adicional) e PIDs vindos da release aprovada;
   - ambiente vazio, sem montagens do host; imagem resolvida pelo ID/digest local; pull desabilitado por padrão;
   - recursos rotulados (`io.cecyber.appsec-labs.platform`); o adapter nunca manipula contêiner sem o rótulo.
4. **Endpoint interno.** O IP:porta da aplicação na rede da sessão é gravado em `runtime_instances` (migração `0002`) para uso exclusivo do gateway; nunca é devolvido ao navegador.
5. **Conteúdo permitido.** Laboratórios benignos ou de autoria da equipe, executados na máquina do próprio desenvolvedor. Aplicações vulneráveis do MVP (LAB-001+) podem rodar assim **apenas localmente**, nunca expostas em rede pública ou compartilhada.

## Consequências

+ Experiência visual testável na máquina do PO antes da infraestrutura on-prem.
+ A suíte de contrato do `RuntimePort` passa a rodar contra um runtime real (`DOCKER_CONTRACT_TESTS=1`, também no CI).
− Os testes comprovam os controles acima, **não** isolamento contra código hostil (SEC-02–14 continuam não executados).
− Imagens de laboratório locais têm ID dependente do build; a release local registrada aponta para o ID local (`scripts/lab-local.sh`/`.ps1`). Se a imagem mudar, é preciso recriar o banco local, pois releases são imutáveis.
− `reset` ainda não suportado neste adapter (IMP-206).

## Reavaliação

Ao concluir a PoC de ADR-001/002: o adapter de produção deve passar na mesma suíte de contrato; este adapter permanece apenas como ferramenta de desenvolvimento.
