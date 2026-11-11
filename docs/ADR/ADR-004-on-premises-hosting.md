# ADR-004: Hospedagem inicial on-premises

| Campo | Valor |
|---|---|
| Data | 2026-11-11 |
| Estado | Decisão de produto registrada; detalhes técnicos pendentes de PoC |
| Decisor | Product Owner |

## Contexto

O CECyber AppSec Labs executará código não confiável e aplicações intencionalmente vulneráveis. O Product Owner escolheu **on-premises** como ambiente de hospedagem inicial. A escolha impacta segurança, capacidade, operação, observabilidade e custos de hardware.

## Decisão

A primeira implantação e o piloto serão planejados para datacenter/infraestrutura própria. Manter interface de provisionamento abstrata e imagens OCI para futura portabilidade, sem assumir que a adoção futura de cloud é obrigatória. Não assumir cluster Kubernetes disponível antes do inventário físico e da PoC.

## Topologia preliminar

- **Zona administrativa:** frontend/API, banco PostgreSQL, registry privado, filas, logs, métricas e validadores. Separar rede e credenciais da zona de laboratório.
- **Zona sandbox:** nós dedicados para workloads de alunos, políticas de rede e egress deny por padrão, sem rotas à rede corporativa/management/backup.
- **Gateway:** proxy autenticado que permite somente tráfego originado em sessões autorizadas.
- **Persistência:** dados acadêmicos no PostgreSQL e volumes efêmeros independentes por laboratório. Backup e restore testados.
- **Validação:** runner isolado com acesso estritamente controlado a snapshots/serviços e sem confiar na máquina do aluno.

## Alternativas a avaliar na PoC

1. K8s on-prem com `RuntimeClass` + gVisor/Kata ou tecnologia equivalente validada.
2. MicroVMs por sessão para perfis de risco elevado.
3. Orquestrador mais simples apenas se demonstrar isolamento, lifecycle e observabilidade exigidos.

Não aprovar `docker.sock` do host exposto, privileged containers por padrão, rede flat com acesso ao controle, mounts de credenciais administrativas nem validadores secretos no sandbox.

## Critérios para aprovação técnica

Inventário CPU/RAM/disco/rede, hipervisor e nós disponíveis; testes de 30 sessões, P95 provisionamento, egress, isolamento entre alunos, tentativa de escape, falha de host, limpeza e backup. Definir equipe de operação, janelas de manutenção e custos elétricos/hardware/licenças.

## Consequências

+ Maior controle de dados e da infraestrutura.
+ Portabilidade preservada via contratos declarativos.
- Exige capacidade operacional própria e investimento em isolamento/segurança física e lógica.
- Elasticidade limitada pelo hardware disponível.

## Pendências

Modelo de servidores, topologia VLANs/firewall, storage, SO, hipervisor, política de atualização, disaster recovery, orçamento e meta definitiva de simultaneidade.
