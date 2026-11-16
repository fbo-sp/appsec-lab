# ADR-023: Validador com cabeçalhos, captura de valor, upload e inspeção do banco

- **Status:** Aceito pelo PO quanto à inspeção do banco (2026-11-16, card "Inspecionar o banco na cópia isolada"); demais extensões registradas pela engenharia.
- **Data:** 2026-11-16
- **Relacionados:** ADR-010 (validação local), ADR-015 (verificações autenticadas), FR-043

## Contexto

As famílias A2 (CSRF), A3 (upload) e A4 (senha) precisam de verificações que o probe HTTP não fazia: usar o token anti-CSRF que a própria página entrega, enviar um arquivo, conferir cabeçalhos de resposta e confirmar que o banco guarda só hashes fortes, o que não se vê por HTTP.

## Decisão

1. **`HttpCheck.expect_headers`**: nome do cabeçalho (sem diferenciar maiúsculas) → trecho exigido no valor (sem diferenciar maiúsculas). Ausência reprova.
2. **`HttpCheck.capture`**: variável → regex com um grupo aplicada ao corpo de uma resposta aprovada. As verificações seguintes usam `{{variavel}}` em path, form, json, headers e conteúdo do arquivo. Variável inexistente ou captura sem casamento reprovam (fail closed). As variáveis valem entre usuários, o que permite testar "token de outra sessão".
3. **`HttpCheck.multipart`**: `{field, filename, content_type, content}`, com `form` como campos extras.
4. **`HttpSuite.inspections` (`InspectCheck`)**: depois das verificações HTTP, o worker lê o arquivo SQLite da cópia isolada com `cat` da imagem (raiz somente leitura, sem shell, usuário do lab, diretório `/`), nunca com código do workspace. A análise roda num contêiner efêmero confiável **sem rede** (`inspect_db.py`, stdlib, `python -I`): a consulta devolve `(chave, valor)`; regras `min_rows`, `all_match`, `none_match` e `verify_passwords`, que confere o hash no formato do Werkzeug (`scrypt:`/`pbkdf2:`) com a senha fictícia. Erro de leitura reprova as inspeções, sem virar ERROR.
5. **Digest das suítes antigas preservado**: os campos novos ficam fora do `suite_digest` quando vazios.

## Consequências

- Cada inspeção aparece como um critério na tela de validação, como as verificações HTTP.
- Limitação: só arquivos de até 8 MiB e sem diário WAL; os labs gravam o banco em `/tmp` com o diário padrão.
- XSS continua validado pelo texto da resposta (com vários payloads e checagem do uso legítimo); um navegador headless no validador fica fora do MVP (FR-043 registra a preferência por avaliação comportamental).
- Testes: unidade do probe (captura, cabeçalhos, multipart), da inspeção (formatos, rejeições, arquivo ausente ou corrompido) e testes Docker reais dos labs que usam as extensões.
