# ADR-027: Validador que lê a resposta de redirecionamento (`no_redirect`)

- **Status:** Registrado pela engenharia (extensão do probe, labs das lacunas dos cursos OWASP). Não altera decisões aprovadas; estende ADR-023 e ADR-024.
- **Data:** 2026-11-17
- **Relacionados:** ADR-015 (verificações autenticadas), ADR-023 (cabeçalhos), ADR-024 (cabeçalhos proibidos)

## Contexto

A família L3 (sessão sem proteção no transporte, OWASP A02:2021 / A04:2025, CWE-614 e CWE-1004) valida as flags do cookie de sessão (`Secure`, `HttpOnly`, `SameSite`) e o cabeçalho HSTS. O cookie de sessão nasce na resposta do login, que é um `302` para o painel. O probe seguia sempre os redirecionamentos e lia só os cabeçalhos da resposta final (limite já registrado no ADR-024), então o `Set-Cookie` do login nunca chegava à verificação.

Também não dava para ler o cookie numa página autenticada seguinte: depois da correção, o cookie tem `Secure`, e o `CookieJar` do probe (como um navegador) não o devolve por HTTP, então a sessão do probe não continuaria autenticada.

## Decisão

1. **`HttpCheck.no_redirect`** (padrão `False`): quando verdadeiro, o probe não segue o `Location`; o status (`302`, `303`...) e os cabeçalhos da própria resposta 3xx são verificados com as regras de sempre (`expect_status_in`, `expect_headers`, `expect_absent_headers`).
2. **Mesmo cliente e mesmos cookies**: a requisição usa o mesmo `CookieJar` do usuário (ou o cliente anônimo), só sem o tratador de redirecionamento.
3. **Digest das suítes antigas preservado**: `no_redirect` entra em `_OPTIONAL_KEYS` e fica fora do `suite_digest` quando falso. Conferido: os digests de todas as suítes registradas antes desta mudança são idênticos.

## Consequências

- Flags de cookie e cabeçalhos de segurança da resposta de login passam a ser validáveis de forma determinística, sem navegador headless.
- Testes: unidade do probe (sem seguir, o `Set-Cookie` do 302 é lido; seguindo, não é; digest igual com o padrão) e testes Docker da família L3.
- Limite: o laboratório não tem TLS real. O HSTS e a flag `Secure` são verificados como cabeçalhos; certificado e redirecionamento para HTTPS ficam no balanceador (fora do lab) e, para o mobile, no MOB-13 (ADR-025).
