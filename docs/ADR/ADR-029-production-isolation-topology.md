# ADR-029: Substrato de isolamento e topologia de produção (Proxmox, 100 sessões simultâneas)

- **Status:** Proposto. Recomendação técnica da engenharia, **pendente de PoC** e do parecer de Segurança e Operações exigidos pelos ADR-001, ADR-002 e ADR-004. Não é decisão aceita.
- **Data:** 2026-11-18
- **Decisores:** Product Owner, Arquitetura, DevSecOps, Segurança e Operações (a confirmar)
- **Relacionados:** ADR-001 (runtime), ADR-002 (isolamento), ADR-004 (on-premises), ADR-008 (runtime Docker só local), ADR-009 (gateway), ADR-011 (métricas de provisionamento), ADR-014 (sessão ociosa), `07_THREAT_MODEL.md` (TM-04, TM-05, TM-06, TM-11, TM-14), NFR-001 a NFR-007 e NFR-015

## Contexto

O hipervisor disponível on-premises é o **Proxmox VE**. O Product Owner definiu em 2026-11-18 a meta de **até 100 laboratórios simultâneos** em produção (o NFR-003 pede 30 no piloto; o ADR-004 deixava a meta definitiva pendente). A pergunta foi: orquestrar os contêineres dos labs **diretamente no Proxmox** ou rodar uma **VM Linux com os contêineres dentro**?

Fatos que pesam na escolha:

1. Todo usuário de lab é tratado como adversário (07 §1), e vários labs dão execução de comandos de propósito (LAB-004 e famílias de injeção de comandos, terminal em todos os labs). Escape de sandbox é **bloqueador do piloto** (07 §6).
2. Os contêineres nativos do Proxmox são **LXC**: compartilham o kernel do **próprio nó do hipervisor**. As versões recentes do Proxmox criam LXC a partir de imagens OCI, mas como recurso em prévia técnica, e o resultado continua sendo LXC.
3. O produto é construído sobre **imagens OCI** e sobre a interface `RuntimePort` (`apps/backend/app/runtime/port.py`: `provision`, `inspect`, `reset`, `terminate`, `list_owned`, `ref_for`, `endpoint`). O adapter atual (`docker_local.py`, ADR-008) já aplica rede interna por sessão, usuário 10001, raiz somente leitura, limites de CPU/memória/PIDs, healthcheck e contêiner de avaliação separado, mas é **só local/teste**: `Settings` recusa esse adapter em produção de propósito.
4. O ADR-004 exige zona sandbox em **nós dedicados**, separada da zona administrativa, e proíbe `docker.sock` exposto, contêiner privilegiado e rede plana até o controle.

## Decisão proposta

1. **Não orquestrar os labs como LXC no Proxmox.** Um escape de LXC atinge o hipervisor e, com ele, a zona administrativa e todas as VMs. Também exigiria descartar o modelo OCI e o adapter existentes.
2. **O Proxmox fornece VMs KVM; os labs rodam como contêineres OCI dentro delas.** A VM é a fronteira forte (virtualização por hardware): um escape fica preso numa VM descartável e reconstruível.
3. **Pool de VMs sandbox, não uma VM única.** De 3 a 5 VMs de labs, para:
   - limitar o raio de um escape a uma fração das sessões;
   - aplicar correção de kernel de forma rolante, drenando uma VM por vez (risco residual de kernel, 07 §7);
   - tolerar a falha de uma VM ou de um nó físico (NFR-006).
4. **Isolamento forte por sessão como padrão.** Todos os labs do catálogo expõem terminal com shell real (`interfaces: [editor, terminal, web]`), então **toda sessão executa código arbitrário** de um usuário tratado como adversário, não só os labs de injeção de comandos. Por isso:
   - **padrão para todas as sessões:** micro-VM por sessão (**Kata Containers**) ou **gVisor**, dentro das VMs sandbox (alternativa 2 do ADR-004), somada ao endurecimento do contêiner (sem root, `cap_drop=ALL`, `no-new-privileges`, seccomp e AppArmor, raiz somente leitura, userns-remap, quotas, rede interna sem egress);
   - **exceção:** contêiner endurecido sem micro-VM só para um lab sem terminal e sem execução de código do aluno, justificado caso a caso;
   - **Kata × gVisor:** o gVisor intercepta as chamadas de sistema num kernel em espaço de usuário, mas ainda roda sobre o kernel da VM; o Kata dá um kernel próprio por sessão e resiste melhor a falhas de kernel, com mais memória por sessão. A escolha sai da PoC (isolamento, compatibilidade com os labs Node e Flask, tempo de início, consumo).
   - Alternativa equivalente a avaliar na mesma PoC: **Kubernetes on-prem com `RuntimeClass` gVisor/Kata** sobre as mesmas VMs (alternativa 1 do ADR-004), se a operação preferir orquestração e observabilidade prontas.
5. **Novo adapter de produção** do `RuntimePort` (Docker-em-VM com runtime Kata/gVisor, ou Kubernetes), que passe na **mesma suíte de contrato** do adapter local e nos testes SEC-01 a SEC-14 do modelo de ameaças. O adapter local continua restrito a desenvolvimento (ADR-008). Os contratos acadêmicos não mudam (NFR-015).
6. **Controle de simultaneidade no plano de controle** (implementação futura, com ADR próprio quando for feita):
   - **admissão** na criação da sessão (`POST /api/v1/sessions`): recusar com 429 e mensagem clara, ou pôr em fila, acima do teto global (100), da capacidade da VM escolhida e das cotas;
   - **cotas:** uma sessão ativa por aluno; teto por turma; kill switch por turma e global (07 §7);
   - **agendamento** das sessões entre as VMs do pool, pelo espaço livre de memória;
   - **liberação de vaga:** TTL da sessão e encerramento por ociosidade de 15 min (ADR-014), mais reconciliação de órfãos (TM-14);
   - **métricas:** sessões ativas por VM, fila, recusas por teto e tempo REQUESTED → READY (ADR-011).

## Topologia proposta

```
                    Proxmox VE (cluster de nós físicos)
 ┌──────────────── VLAN admin ────────────────┐   ┌──────── VLAN sandbox (sem rota para admin/corporativa/backup) ────────┐
 │ VM controle: portal, API, worker, gateway  │   │ VM labs 1   VM labs 2   VM labs 3   (… até 5)                       │
 │ VM dados: PostgreSQL (+ backup)            │   │ contêineres OCI por sessão; Kata/gVisor nos labs de risco alto     │
 │ VM registry privado de imagens             │   │ rede interna por sessão, egress negado                            │
 └────────────────────────────────────────────┘   └─────────────────────────────────────────────────────────────────────┘
          gateway autenticado (ADR-009) é a única ponte do aluno até a VLAN sandbox;
          a API fala com o runtime das VMs por canal autenticado, nunca por docker.sock exposto na rede.
```

## Dimensionamento inicial (a confirmar na PoC)

Base: teto declarado nas releases atuais, 0,5 vCPU, 512 MiB, 64 PIDs e 256 MiB de disco por sessão, TTL de 45 min.

| Recurso | Pior caso com 100 sessões | Proposta |
|---|---|---|
| Memória (limite rígido) | 100 × (512 MiB do lab + ~150 a 250 MiB da micro-VM Kata) ≈ 65 a 75 GiB, mais os contêineres de avaliação e o SO das VMs | 96 a 128 GiB na zona sandbox, divididos entre as VMs (ex.: 4 VMs × 32 GiB); com gVisor o overhead é menor |
| CPU | 100 × 0,5 = 50 vCPU de limite; uso real é oscilante | 24 a 40 núcleos físicos na zona sandbox, com overcommit moderado |
| Disco | volumes efêmeros pequenos + imagens dos ~100 labs em cache | SSD local nas VMs sandbox; imagens puxadas do registry privado |
| Zona admin | API, worker, gateway, PostgreSQL, registry | 8 vCPU e 16 GiB no controle; dados e registry à parte |

O overhead da micro-VM vale para as 100 sessões, porque o isolamento forte é o padrão: medir na PoC e ajustar o pool.

## Checklist da PoC

Ambiente mínimo: 1 VM de controle e 2 VMs sandbox no Proxmox, VLANs separadas.

**Inventário (ADR-004)**
- [ ] Nós físicos, CPU, RAM, disco, rede e versão do Proxmox disponíveis.
- [ ] Plano de VLANs e firewall (admin, sandbox, saída), sem rota da sandbox para admin, corporativa e backup.
- [ ] SO das VMs, política de atualização, janelas de manutenção e equipe de operação.

**Isolamento (ADR-002, TM-04, TM-05, TM-06)**
- [ ] O catálogo inteiro (101 labs: Flask, Node, mobile simulado) sobe com Kata e com gVisor como padrão; anotar incompatibilidades.
- [ ] Tentativas de escape a partir do terminal do lab (montagens, syscalls, `/proc`, capabilities) não atingem a VM nem o hipervisor.
- [ ] Sessão A não alcança sessão B, a API, o PostgreSQL, o DNS interno nem 169.254.169.254 (SEC-04, SEC-06).
- [ ] Nenhum `docker.sock`, credencial de controle ou segredo do validador dentro do lab (SEC-07).

**Capacidade e desempenho (NFR-003, NFR-004, NFR-005)**
- [ ] 30 sessões simultâneas e depois 100: P95 REQUESTED → READY ≤ 60 s; ≥ 98% chegam a READY.
- [ ] Consumo real de memória e CPU por sessão (contêiner, Kata, gVisor) e o overhead × 100 sessões, para fechar o dimensionamento.
- [ ] Fork bomb, consumo de CPU e disco cheio ficam contidos na sessão (SEC-11).

**Operação e resiliência (NFR-006, NFR-007, TM-14)**
- [ ] Desligar uma VM sandbox com sessões ativas: plataforma continua, sessões afetadas encerram de forma limpa, resultados preservados (NFR-008).
- [ ] Correção de kernel rolante: drenar uma VM, atualizar e devolver ao pool sem parar as demais.
- [ ] Limpeza: 100% das sessões expiradas sem contêiner, rede ou volume órfão, inclusive após queda do worker.
- [ ] Backup e restore do PostgreSQL testados.

**Simultaneidade**
- [ ] Protótipo da admissão: 101ª sessão recusada com mensagem clara; uma sessão por aluno; vaga liberada no encerramento por ociosidade.

**Evidências para aceite**
- [ ] Relatório da PoC com ambiente, versões, digests das imagens e resultados de SEC-01 a SEC-14.
- [ ] Comparação Kata × gVisor × Kubernetes com `RuntimeClass` (isolamento, início, consumo, operação).
- [ ] Parecer de Segurança e Operações; atualização dos ADR-001, ADR-002 e ADR-004 com a decisão.

## Consequências

+ Duas barreiras para o código do aluno: a micro-VM da sessão e a VM sandbox descartável; o hipervisor e a zona administrativa ficam fora de alcance.
+ Preserva o modelo OCI, a interface `RuntimePort`, o gateway e as imagens dos 101 labs.
+ Pool de VMs permite manutenção rolante e tolerância a falhas.
- Exige escrever e testar o adapter de produção e operar Kata ou gVisor.
- Duas camadas de virtualização (KVM e micro-VM em todas as sessões) custam memória e tempo de início, a medir na PoC.
- Capacidade limitada pelo hardware on-premises; crescer além de 100 sessões pede mais VMs no pool e ajuste do teto.
