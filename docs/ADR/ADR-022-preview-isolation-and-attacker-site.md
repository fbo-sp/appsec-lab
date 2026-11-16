# ADR-022: Isolamento do preview para labs com JavaScript de ataque e site do atacante

- **Status:** Aceito pelo PO quanto ao site do atacante (2026-11-16, card "Página do atacante em outro host"); detalhe técnico abaixo registrado pela engenharia.
- **Data:** 2026-11-16
- **Relacionados:** ADR-008 (runtime local), ADR-009 (gateway), TM-13 (CSRF e origem)

## Contexto

Os labs de XSS, upload com stored XSS e CSRF executam, de propósito, JavaScript de ataque no navegador do aluno. O portal (8000), o workspace (8001) e o preview (8002) ficam em `127.0.0.1`, e para o navegador portas diferentes são o **mesmo site** (cookies não se separam por porta, e `SameSite` não distingue portas). Era preciso confirmar que o JavaScript que roda na origem do preview não alcança o portal nem o workspace, e decidir de onde parte o ataque de CSRF.

## Decisão

1. **Isolamento confirmado por teste, sem mudança de arquitetura.** O ADR-009 já separa as origens: a API do workspace exige o cabeçalho `X-Cecyber-Workspace` (força preflight CORS, que o gateway não aprova), o terminal exige `Origin` igual à do workspace, os grants são HttpOnly e `SameSite=Strict`, e a API do portal não habilita CORS. Testes novos simulam o JavaScript do preview: o preflight para a API do workspace não recebe permissão, a requisição simples é negada (403) e o WebSocket do terminal recusa a origem do preview.
2. **Site do atacante em origem própria** (`:8003`, configurável por `GATEWAY_ATTACKER_URL`). Só existe para variantes com a interface `attacker` no manifesto. O gateway serve a porta **8090** do contêiner do lab, onde o próprio lab publica páginas estáticas fictícias (fora do workspace). Acesso por ticket de uso único (`purpose=attacker`), emitido só ao dono, trocado por grant `cecyber_at` (HttpOnly, `SameSite=Strict`). O site do atacante só aceita GET/HEAD, não recebe nenhum cookie do navegador e não pode ser enquadrado (`frame-ancestors 'none'`). O gateway informa a origem do preview à página por `?alvo=`.
3. **Mesmo site, origem diferente.** Uma página em outro *site* (outro nome de host) não conseguiria alcançar o preview: o grant do preview é `SameSite=Strict` e não acompanha navegação vinda de outro site, o que é uma proteção que não queremos afrouxar. Por isso o site do atacante fica em outra **origem** do mesmo site, como um subdomínio ou sistema comprometido da mesma empresa. A lição dos labs de CSRF fica correta: `SameSite` não protege contra páginas do mesmo site; o **token anti-CSRF** protege.
4. O portal mostra o botão **site do atacante** na aba Aplicação quando a variante tem a interface `attacker`; ele abre a página numa nova aba, como um link recebido por e-mail.

## Consequências

- Contrato: `Interface.ATTACKER`; `interfaces` aceita até 4 itens.
- Backend: `Purpose.ATTACKER`, `gateway_attacker_url`, `build_gateway_apps` com a terceira origem, `interfaces` na visão da sessão e das variantes, recusa `ATTACKER_SITE_UNAVAILABLE` (409).
- Compose publica `127.0.0.1:8003`. Continua válido só para o runtime local (ADR-008).
- Limitação: o alerta `alert()` não aparece no preview, porque o iframe não tem `allow-modals`; os labs de XSS usam um marcador visível na página em vez de `alert()`.
