# Central de Documentos · Corrente Energia (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **path traversal** (travessia de diretório) para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/painel_controller.py` — a área logada e a rota `/documento`, que baixa um documento
  pelo nome informado.
- `services/documento_service.py` — **a leitura do documento**. Monta o caminho e abre o arquivo.
  É aqui que falta conferir se o caminho fica dentro da pasta de documentos. É aqui que está a falha.
- `documentos/` — os documentos que o usuário pode baixar. `segredo_interno.txt` (fora dessa pasta)
  simula um arquivo interno que **não** deveria ser acessível.
- `services/auth_service.py` — login (não é o foco; as senhas já usam hash forte).

## A feature

O usuário vê a lista dos próprios documentos e baixa um deles pela rota `/documento?nome=...`. O
serviço junta a pasta de documentos com o nome recebido e abre o arquivo. Se não conferir o caminho
final, um nome como `../segredo_interno.txt` — ou um caminho absoluto — faz a leitura **sair** da
pasta e devolver arquivos que não deveriam ser acessíveis. A defesa é garantir que o caminho final
continue **dentro** da pasta de documentos.
