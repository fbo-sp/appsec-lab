# Família `upload` (A3): upload irrestrito levando a XSS armazenado

Gera LAB-014 (A3-FIN, Cooperativa Credimova), LAB-015 (A3-SAU, Clínica Sampaio) e LAB-016 (A3-IND,
Siderúrgica Pindorama). ADR-021 descreve o modelo de família.

## Código-base comum (`modelo/`)

Aplicação Flask em camadas (controllers, services, repositories, models) com um envio de anexos: um
usuário comum anexa [[um_documento]] e a equipe interna abre os arquivos na `/mesa`.

Vulnerabilidade intencional:

- `services/anexo_service.py` aceita o arquivo pelo **`Content-Type` informado no envio** (não pelo
  conteúdo) e o guarda com o nome original; `controllers/anexo_controller.py` serve o arquivo em
  `/anexos/<nome>` sem `nosniff`. Um `.html` disfarçado de imagem é então servido como `text/html` e
  executa na origem da aplicação (CWE-434 levando a XSS armazenado, CWE-79).

### Demonstração inofensiva (decisão do PO, 2026-11-16)

O arquivo `amostras/comprovante.html` **não** lê nem envia dado nenhum: só escreve um aviso "XSS-OK" na
página, provando que o navegador o executou. A lição (a vulnerabilidade e a correção) é idêntica à de um
PoC que roubasse a sessão; a carga foi mantida inofensiva de propósito, por restrições de segurança do
ambiente de geração do laboratório. A etapa 3 do manifesto traz uma nota explicando isso ao aluno, sem
citar fornecedor.

Correção esperada: validar pela **assinatura** do conteúdo (magic number), guardar com nome gerado
(`uuid4().hex` + extensão) e acrescentar `X-Content-Type-Options: nosniff` no download.

A suíte `upload/python-flask/file-upload-<ramo>-v1` (ADR-023) envia um PDF de verdade (aceito), um HTML
disfarçado de `image/png` (deve ser recusado), confere o `nosniff` no download e **inspeciona o banco da
cópia** para garantir que nenhum anexo foi guardado como `.html`. Os testes com Docker real estão em
`apps/backend/tests/test_upload_family_validation.py`.

## O que muda por ramo (`ramos.yaml`)

Empresa, história, documento do domínio (comprovante de renda, pedido médico, nota fiscal), rota, mesa da
equipe, usuários fictícios e o anexo semeado. Os valores que a suíte usa (login comum, rota, nome do
banco, anexo semeado) ficam também em `UPLOAD_RAMOS`, no registro protegido
(`apps/backend/app/validation/suites_familias.py`); os dois têm de bater.

## Gerar de novo

```bash
uv run python scripts/gerar-familia.py upload       # regrava LAB-014..016
uv run python scripts/gerar-familia.py --check --all  # o mesmo teste da CI
```

Não edite as pastas `LAB-01N-*` à mão. Uma mudança no modelo que altera o lab publicado exige versão
nova no manifesto (release imutável) e entrada em `docs/catalogo/historico-versoes.yaml`.
