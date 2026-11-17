# ADR-024: Validador com cabeçalhos proibidos (`expect_absent_headers`)

- **Status:** Registrado pela engenharia (extensão do probe, 2ª leva de labs). Não altera decisões aprovadas; estende ADR-023.
- **Data:** 2026-11-17
- **Relacionados:** ADR-023 (cabeçalhos, captura, upload, inspeção), ADR-021 (famílias)

## Contexto

Famílias da 2ª leva têm vulnerabilidades cujo sinal de correção é a **ausência** (ou o valor seguro) de um cabeçalho de resposta, não a sua presença:

- **A7 CORS mal configurado**: a aplicação vulnerável reflete qualquer `Origin` em `Access-Control-Allow-Origin` (com `Access-Control-Allow-Credentials: true`); a correção para de refletir origem não confiável. O sinal é "o cabeçalho **não** devolve a origem maliciosa".
- Outras famílias previstas (flags de cookie, injeção de cabeçalho/CRLF, cabeçalhos de erro verbosos) têm o mesmo formato.

O probe (ADR-023) só sabia **exigir** um trecho num cabeçalho (`expect_headers`); não sabia **proibir** um trecho, nem exigir um cabeçalho ausente. Reescrever o sinal no corpo seria artificial e não ensinaria o aluno a olhar o cabeçalho certo.

## Decisão

1. **`HttpCheck.expect_absent_headers`**: nome do cabeçalho (sem diferenciar maiúsculas) → trecho que **não** pode aparecer no valor (sem diferenciar maiúsculas). É o espelho de `not_contains` para cabeçalhos. Trecho **vazio** (`""`) exige o cabeçalho **totalmente ausente**. Cabeçalho ausente nunca reprova por esta regra (nada proibido pode estar presente).
2. **Substituição de variável**: como os demais campos, passa por `{{variavel}}` (ADR-023) antes da verificação.
3. **Digest das suítes antigas preservado**: `expect_absent_headers` entra em `_OPTIONAL_KEYS`, então fica fora do `suite_digest` quando vazio; nenhuma suíte anterior muda de digest.

## Consequências

- A família A7 (e as seguintes de mesmo formato) passa a ser validável de forma determinística e fiel, premiando a correção de livro (parar de refletir/omitir o cabeçalho), sem navegador headless.
- Testes: unidade do probe (cabeçalho proibido presente reprova; ausente aprova; trecho vazio exige ausência) e testes Docker reais das famílias que usam a extensão.
- Limitação: o probe (como antes) lê cabeçalhos da resposta final após redirecionamentos; checagens de CORS usam requisições diretas ao endpoint de API, sem redirecionamento.
