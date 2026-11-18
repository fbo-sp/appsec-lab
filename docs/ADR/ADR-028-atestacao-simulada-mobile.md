# ADR-028: Serviço de integridade da loja simulado no laboratório de app adulterado

- **Status:** Registrado pela engenharia (família L11 `mob-app-adulterado`, labs das lacunas dos cursos OWASP). Estende o ADR-025 (labs mobile simulados); não altera decisões aprovadas.
- **Data:** 2026-11-17
- **Relacionados:** ADR-008 (runtime Docker local), ADR-021 (famílias), ADR-025 (labs mobile)

## Contexto

O Mobile Top 10 2016 M8 (Code Tampering) e o 2024 M7 (Insufficient Binary Protections) pedem que o servidor não confie no app, que pode ser modificado e reempacotado, e que use atestação da plataforma (Play Integrity, App Attest). O laboratório não tem emulador nem loja: o app é um cliente web simulado (ADR-025).

## Decisão

1. **A "adulteração" é editar o código do app** no workspace (`static/regras.js`), que faz o papel do APK/IPA.
2. **A loja é simulada no servidor** (`services/atestacao_service.py`, sem falha): o selo é um JSON (conta, veredito, validade de 120 s) assinado com HMAC. O veredito é `app_oficial` se o hash de `static/app.js` + `static/regras.js` bate com o do pacote oficial, senão `app_modificado`.
3. **Hash oficial e chave ficam fora do workspace**, em `/opt/loja`, gerados no build da imagem (chave aleatória por build), somente leitura.
4. **A suíte** confere: conta avançada com selo válido passa; conta básica que se declara avançada, pedido sem selo, selo forjado e selo de outra conta são recusados. Com `regras.js` ainda modificado, a própria conta avançada é recusada (o aluno desfaz a alteração antes de validar).

## Consequências

- A lição (regra no servidor, selo conferido no servidor) é validada de forma determinística, sem emulador.
- Limite: o processo do lab lê a chave em `/opt/loja`, então um aluno poderia forjar selos lendo-a. Na plataforma real o servidor verifica com a API ou a chave pública da loja, e o app nunca tem a chave. O texto do lab explica a diferença.
