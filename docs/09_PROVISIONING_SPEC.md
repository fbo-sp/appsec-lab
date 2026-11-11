# 09. Provisionamento e Isolamento

| Campo | Valor |
|---|---|
| Versão | 0.2.0 |
| Estado | Desenho proposto, bloqueado por PoC de isolamento |
| Referências | `07_THREAT_MODEL.md`; FR-020–027; NFR-001–005/007/012; ADR-001/002 |

## 1. Princípios

Criar sandbox **por sessão**, efêmero, sem acesso direto ao plano de controle, sem credenciais reais, com imagem de lab por digest e política explícita. Kubernetes é um candidato de orquestração, não fronteira de isolamento suficiente por si só. Perfil de execução seguro deverá ser selecionado depois de testar gVisor/Kata ou alternativa de microVM. LAB-004 é bloqueado até aprovação do sandbox.

## 2. Provisioning request (contrato conceitual)

```yaml
sessionId: "<uuid>"
labVersionId: "LAB-001@1.0.0"
imageDigest: "sha256:<real-digest>"
profile: web-terminal-editor
policyRef: sandbox-hardened-v1
resources:
  cpuMillicores: 500
  memoryMiB: 512
  pidsMax: 128
  ephemeralStorageMiB: 1024
network:
  egressProfile: deny-all
  exposedInternalPorts: [5000]
lease:
  expiresAt: "2026-11-11T23:00:00Z"
```

Campos não são aceitos diretamente do navegador; recursos e perfis são resolvidos de manifesto **aprovado** e política server-side. Validar allowlists; nunca aceitar `hostPath`, capabilities, privileged, imagens ou portas arbitrárias enviadas pelo aluno.

## 3. Política de workload

- Namespace/pool de execução segregado, labels com session_id opaco, owner reference/finalizer controlado e políticas de admission.
- `runAsNonRoot`, `allowPrivilegeEscalation: false`, capabilities drop ALL, seccomp RuntimeDefault ou perfil aprovado, filesystem raiz somente leitura conforme compatibilidade e no host PID/IPC/network.
- Desabilitar montagem de service account (`automountServiceAccountToken: false`); não anexar credenciais do registry ou de controle ao contêiner do aluno.
- Resource requests/limits e quotas de namespace, pids, armazenamento efêmero e número de sessões; health probes com timeouts.
- NetworkPolicy default-deny + camada de enforcement adicional (CNI/host/firewall) testada. Restringir DNS; bloquear metadata e RFC1918 quando não estritamente necessário. Gateway é único ponto autorizado de entrada para editor/terminal/app.
- Downloads de dependências durante sessão desabilitados por padrão. Pacotes pré-bakeados na imagem ou mirror dedicado aprovado; nenhum acesso irrestrito à Internet.
- Não admitir LAB-004 num cluster que compartilhe recursos críticos sem comprovação de contenção adequada.

## 4. Operações do adaptador

| Método | Comportamento | Compensação |
|---|---|---|
| `provision` | valida digest/política, cria recursos com nome determinístico, aguarda readiness | rollback/reconcile se criação parcial |
| `inspect` | retorna health, phase, motivo sanitizado, métricas | retornar UNKNOWN e retry se orquestrador indisponível |
| `reset` | revoga conexões, recria workspace/app com mesma versão | preserva resultado acadêmico, nova revision |
| `terminate` | revoga gateway, apaga workloads, volumes e regras transitórias | repetir até confirmar ausência |
| `list_owned` | lista workloads por label/owner da plataforma | alimenta cleanup órfão |

## 5. Ciclo de vida técnico

1. Reservar quota atomically no banco de controle; emitir outbox.
2. Worker chama adapter com `session_id`; criar recursos por nomes estáveis sem duplicar em retry.
3. Aguardar readiness de app e workspace, testar gateway, registrar runtime_ref.
4. Abrir acesso mediante grant curto e audience específico; WebSockets sujeitos a reautorização/revogação.
5. Monitorar `expires_at` independentemente de navegação. Se atingir limite, negar acesso primeiro, depois remover workload/volumes/regras.
6. Reconciliador compara database e cluster; recurso órfão ou state divergente dispara correção e auditoria.

## 6. Gateway seguro

- Rotear por `session_id` autenticado a runtime_ref resolvido no backend, não pelo parâmetro de URL/host do usuário.
- Terminação TLS, validação Origin e upgrade WS, autorização de sessão e finalidade (editor/terminal/app), timeouts, limite de conexões e logs de acesso sem segredos.
- Para a aplicação embutida, considerar subdomínios de origem segregada e proteção contra cookie leakage/cross-origin. Não servir conteúdo vulnerável na mesma origem do painel administrativo.

## 7. Perfis e sizing da PoC

| Perfil | Alvo | Limites iniciais a testar |
|---|---|---|
| `web-basic` | LAB-001/002 | 0.5 vCPU, 512 MiB, 1 GiB armazenamento |
| `api-basic` | LAB-003 | 0.5 vCPU, 512 MiB, 1 GiB armazenamento |
| `exec-restricted` | LAB-004 | >=0.5 vCPU e memória a medir, isolamento reforçado obrigatório |

Metas NFR: 30 sessões simultâneas e P95 REQUESTED→READY <=60 s para labs simples, **a aferir**, considerando cold start, tamanho de imagem, alocação e overhead do runtime. Medir também uso real e custo/hora, sem inferir número de nós pela soma dos limites.

## 8. PoC comparativa e decisão

Executar as mesmas suítes de LAB-001 e cenário de processo adversarial controlado em 2 opções de runtime, sempre em ambiente descartável. Registrar versões, nós, tempo cold/warm startup p50/p95, uso de RAM/CPU, operações de reset/cleanup, comportamento em falhas e testes SEC-04–07/11/14. Escolher primeiro pela contenção, depois pela compatibilidade e operação, finalmente por custo/performance. Atualizar ADR-002 com resultado e sign-off da Segurança.

## 9. Aceite e condições de bloqueio

- PRV-01: 30 sandboxes idempotentes e isoladas no piloto de carga.
- PRV-02: nenhum sandbox alcança API/host/outro sandbox, metadados ou Internet fora da política.
- PRV-03: reinício do worker e quedas de conexão não geram workloads duplicados.
- PRV-04: remoção completa de workload e volume, com evidência e alarmes para órfãos.
- PRV-05: runtime não injeta segredos nem altera imagem publicada.
- PRV-06: LAB-004 só publica após aprovação explícita de Segurança.

**Aberto:** alternativa de sandbox, provedor/infra Kubernetes, decisão de cluster dedicado, parâmetros finais de quota e SLA de cleanup.

## Adendo v0.3: on-premises

Premissa definida: hospedagem inicial on-premises. Provisioning Adapter deve ser testado contra nó/cluster físico próprio, com segmentação rede de gestão vs. rede de laboratórios, sem rotas internas desnecessárias e política egress deny. Não assumir recursos cloud gerenciados; inventário e plano de capacidade são entregáveis obrigatórios antes do piloto. Ver `ADR/ADR-004-on-premises-hosting.md`.
