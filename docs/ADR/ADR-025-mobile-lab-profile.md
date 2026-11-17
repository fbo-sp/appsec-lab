# ADR-025: Perfil mobile dos laboratórios (moldura de celular na aba Aplicação)

- **Status:** Aceito pelo PO quanto à visualização (2026-11-17, "essa visualização está aprovada"); detalhe técnico registrado pela engenharia.
- **Data:** 2026-11-17
- **Relacionados:** ADR-008 (runtime local), ADR-009 (gateway), ADR-019 (Explorar mais), ADR-022 (isolamento do preview), docs/11 (manifesto), docs/21 (experiência de aprendizagem)

## Contexto

A trilha de segurança mobile (OWASP MASVS e Mobile Top 10 2024/2016) precisa parecer, para o aluno, um aplicativo de celular. O PO exigiu que o **layout geral dos labs atuais seja mantido** (topbar, barra da sessão, etapas à esquerda, abas à direita) e que só a aplicação ganhe aparência de celular. Não há emulador Android/iOS: exigiria acesso ao host e fere o ADR-008. O app do lab é um cliente web mobile-first simulado, mais uma API real no contêiner.

## Decisão

1. **Campo novo e opcional `variants[].platform`** com valores `web` (padrão, comportamento atual) e `mobile`. Labs existentes não mudam.
2. Com `platform: mobile`, o portal só altera a **aba Aplicação**: o preview aparece dentro de uma moldura de celular (viewport ~300×620, barra de status, ilha, barra de navegação). Barra de endereço, "i", recarregar, nova aba e "Código + Aplicação" permanecem. Código, Terminal e Validação ficam idênticos.
3. **Aba "Aparelho" (segunda fase).** O protótipo aprovado mostra uma aba somente leitura com dados locais, pacote, log e rede do aparelho. Na primeira leva, o aluno inspeciona esses itens pelo Terminal e pela aba Código (ex.: `cliente/config.json` como o pacote do app, `ver_aparelho.py` para as preferências gravadas). A aba dedicada fica para uma segunda fase, servida pelo gateway a partir de arquivos fictícios do lab, sem execução.
4. A moldura é só apresentação: o isolamento do ADR-022 vale igual (mesmo iframe e sandbox do preview).
5. Etapas, dicas, pontuação, validação por suíte e catálogo seguem iguais. A classificação ganha as listas **OWASP Mobile Top 10 2024** e **2016** (uma linha por lista/versão), além do CWE e do MASVS; o filtro de Classificação passa a reconhecê-las.
6. Itens de formato novo da lista mobile (MOB-13..17: TLS sem validação, pinning, SDK vulnerável, binário sem proteção, revisão Kotlin/Swift) ficam fora deste ADR e exigem decisão própria.

## Consequências

- Contrato: `Platform` enum e `variants[].platform` em `cecyber_contracts`; docs/11 e docs/21 atualizados; schema regenerado.
- Backend: `platform` exposto na visão da variante; sem outra mudança de API.
- Web: moldura de celular na aba Aplicação; `catalogFilter` reconhece "OWASP Mobile Top 10" e "OWASP MASVS".
- Primeira leva: famílias mob-chave-embutida, mob-dados-locais, mob-biometria-cliente, mob-sessao-logout, mob-dados-demais e mob-modo-teste (LAB-050 a LAB-067), app mobile simulado comum, suítes em `suites_familias.py` e testes Docker em `test_mobile_families_validation.py`.
- Limitação: não há comportamento nativo (biometria real, keystore, deep link do SO). O lab simula esses recursos no cliente web e valida a falha no servidor.
