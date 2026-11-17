"""Suítes PROTEGIDAS das famílias de laboratórios por ramo (ADR-021).

Uma família tem a mesma mecânica em vários ramos de atividade; aqui cada família tem uma função que
monta as suítes de um ramo a partir dos dados fictícios desse ramo (rotas, logins, respostas). Os mesmos
valores aparecem no seed de cada lab (``laboratories/_familias/<familia>/ramos.yaml``); os testes Docker
de cada família conferem os dois lados.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import urllib.parse
from dataclasses import dataclass

from app.validation.suites import AnswerSuite, HttpCheck, HttpLogin, HttpSuite, InspectCheck, Suite

# --------------------------------------------------------------------------------------------------
# A1 XSS (LAB-005 a LAB-007)


@dataclass(frozen=True, slots=True)
class XssRamo:
    ramo: str
    rota: str
    comum: tuple[str, str]  # login e senha do usuário comum (fictícios)
    equipe: tuple[str, str]  # login e senha da equipe interna (fictícios)
    cookie_comum: str  # valor do cookie sem HttpOnly do usuário comum
    cookie_equipe: str  # valor do cookie sem HttpOnly da equipe
    termo_legitimo: str
    trecho_legitimo: str  # trecho do item legítimo como aparece no HTML
    nota_seed_outro: str  # observação de outro usuário que o painel continua mostrando


XSS_RAMOS = (
    XssRamo(
        "fin",
        "favorecidos",
        ("marina.costa", "Marina@2026"),
        ("renata.gerente", "Gerente#Aurora26"),
        "AUR-DSP-7Q4M-2210",
        "AUR-APR-5531-KX",
        "D'Ávila",
        "Ávila Ltda",
        "Mensalidade",
    ),
    XssRamo(
        "sau",
        "exames",
        ("julia.andrade", "Julia@2026"),
        ("carla.atendente", "Atende#Lumina26"),
        "LUM-APP-5D2R-8814",
        "LUM-ATD-2290-QZ",
        "25-OH",
        "Vitamina D (25-OH)",
        "Tenho claustrofobia leve",
    ),
    XssRamo(
        "ind",
        "ordens",
        ("tiago.nunes", "Campo@2026"),
        ("helena.cod", "Operador#Volt26"),
        "VOL-TAB-4C7N-6602",
        "VOL-MNB-7718-TW",
        "R-12",
        "Religador R-12 (Alim. 04)",
        "Fusível queimado",
    ),
)

_IMG = '<img src=x onerror="this.outerHTML=document.cookie">'
_ARMAZENADO = '<img src=x onerror=alert("painel-validacao")>'


def _q(rota: str, termo: str) -> str:
    return f"/{rota}?q={urllib.parse.quote(termo)}"


def _xss(r: XssRamo) -> tuple[Suite, ...]:
    def login(nome: str, cred: tuple[str, str]) -> HttpLogin:
        return HttpLogin(name=nome, path="/login", form={"login": cred[0], "senha": cred[1]})

    def refletido(check_id: str, payload: str, tag: str, descricao: str) -> HttpCheck:
        return HttpCheck(
            id=check_id,
            description=descricao,
            path=_q(r.rota, payload),
            as_user="comum",
            contains=("&lt;" + tag[1:],),
            not_contains=(tag,),
        )

    return (
        AnswerSuite(
            ref=f"xss/answer/locate-cleaner-{r.ramo}-v1",
            version="1.0.0",
            prompt="Nome do método que limpa o texto",
            accepted=("limpar_texto", "limpar_texto()", f"{r.rota[:-1]}service.limpar_texto"),
            success_feedback="Isso: é a proteção que o time criou. Na próxima etapa você vai testá-la.",
            failure_feedback="Ainda não. Abra o serviço e procure o método chamado na primeira linha de buscar.",
        ),
        AnswerSuite(
            ref=f"xss/answer/safe-filter-{r.ramo}-v1",
            version="1.0.0",
            prompt="Filtro do Jinja2 que desliga a codificação",
            accepted=("safe", "|safe"),
            success_feedback="Exato: o |safe manda o termo para a página como HTML. Agora vamos executar código.",
            failure_feedback="Não é esse. Procure, no template, o que vem depois do | na linha Resultados para.",
        ),
        AnswerSuite(
            ref=f"xss/answer/client-cookie-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor do cookie lido pelo JavaScript",
            accepted=(r.cookie_comum,),
            success_feedback="Você executou JavaScript sem usar <script> e leu um cookie sem HttpOnly.",
            failure_feedback="Não é esse. Copie só o valor depois do sinal de igual, sem o ponto e vírgula.",
        ),
        AnswerSuite(
            ref=f"xss/answer/staff-cookie-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor do cookie da equipe",
            accepted=(r.cookie_equipe,),
            success_feedback="O código gravado por um usuário comum rodou na tela da equipe. Agora vamos corrigir.",
            failure_feedback="Não é esse. Entre com o usuário da equipe e leia a linha que você cadastrou no painel.",
        ),
        HttpSuite(
            ref=f"xss/python-flask/output-encoding-{r.ramo}-v1",
            version="1.0.0",
            logins=(login("comum", r.comum), login("equipe", r.equipe)),
            checks=(
                refletido(
                    "busca-img-onerror",
                    _IMG,
                    "<img src=x onerror",
                    "A busca mostra <img ... onerror=...> como texto, sem criar a tag.",
                ),
                refletido(
                    "busca-svg-onload",
                    "<svg onload=alert(1)>",
                    "<svg onload",
                    "Outras tags também saem como texto, como <svg onload=...>.",
                ),
                refletido(
                    "busca-details-ontoggle",
                    "<details open ontoggle=alert(1)>",
                    "<details open ontoggle",
                    "Uma lista de bloqueio maior não basta: <details ontoggle=...> também sai como texto.",
                ),
                HttpCheck(
                    id="busca-legitima",
                    description=f"A busca por {r.termo_legitimo} continua encontrando o registro certo.",
                    path=_q(r.rota, r.termo_legitimo),
                    as_user="comum",
                    contains=(r.trecho_legitimo,),
                ),
                HttpCheck(
                    id="cadastro-funciona",
                    description="O cadastro continua funcionando com um texto qualquer no campo livre.",
                    path=f"/{r.rota}/novo",
                    method="POST",
                    as_user="comum",
                    form={"nome": "Validacao XSS", "detalhe": "-", "nota": _ARMAZENADO},
                    contains=("Validacao XSS",),
                ),
                HttpCheck(
                    id="painel-codificado",
                    description="No painel da equipe, o texto gravado aparece como texto, sem executar.",
                    path="/painel",
                    as_user="equipe",
                    contains=("&lt;img src=x onerror=alert(",),
                    not_contains=("<img src=x onerror=alert(",),
                ),
                HttpCheck(
                    id="painel-continua",
                    description="O painel continua mostrando os registros de todos os usuários.",
                    path="/painel",
                    as_user="equipe",
                    contains=(r.nota_seed_outro,),
                ),
                HttpCheck(
                    id="painel-restrito",
                    description="O painel continua restrito à equipe (usuário comum recebe 403).",
                    path="/painel",
                    as_user="comum",
                    expect_status=403,
                ),
            ),
            success_feedback=(
                "Correção validada numa cópia isolada do seu workspace: o texto do usuário agora chega à "
                "página sempre como texto, na busca e no painel."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste os templates e valide de novo."
            ),
        ),
    )


# --------------------------------------------------------------------------------------------------
# A5 Mass Assignment (LAB-008 a LAB-010)


@dataclass(frozen=True, slots=True)
class MassaRamo:
    ramo: str
    login: tuple[str, str]  # usuário comum (fictício)
    perfil_comum: str
    perfil_priv: str
    rota_priv: str
    campo: str  # coluna de negócio que o usuário não pode alterar
    valor_original: str
    valor_ataque: str
    beneficio: tuple[str, ...]  # respostas aceitas para o benefício da etapa 3
    chave_priv: str


MASSA_RAMOS = (
    MassaRamo(
        "fin",
        ("bruno.sales", "Bruno@2026"),
        "cliente",
        "analista",
        "backoffice",
        "pacote",
        "essencial",
        "private",
        ("250000", "250.000", "250.000,00", "r$ 250.000,00", "r$250.000,00", "250 mil"),
        "TRP-LIM-6630-PZ",
    ),
    MassaRamo(
        "sau",
        ("paula.mendes", "Paula@2026"),
        "beneficiario",
        "auditor",
        "auditoria",
        "plano",
        "regional",
        "nacional-premium",
        ("1800", "1.800", "1.800,00", "r$ 1.800,00", "r$1.800,00"),
        "SER-AUD-3381-MV",
    ),
    MassaRamo(
        "ind",
        ("rafael.dutra", "Rafael@2026"),
        "fornecedor",
        "comprador",
        "compras",
        "categoria",
        "padrao",
        "estrategico",
        ("750000", "750.000", "750.000,00", "r$ 750.000,00", "r$750.000,00", "750 mil"),
        "TMV-CMP-9054-RL",
    ),
)

_IGNORADO = (200, 400, 422)  # campo proibido: ignorado (200) ou recusado (400/422), nunca gravado


def _massa(r: MassaRamo) -> tuple[Suite, ...]:
    def json_tem(chave: str, valor: str) -> str:
        return f'"{chave}":"{valor}"'

    def patch(check_id: str, descricao: str, corpo: dict[str, object]) -> HttpCheck:
        return HttpCheck(
            id=check_id,
            description=descricao,
            path="/api/perfil",
            method="PATCH",
            as_user="comum",
            json=corpo,
            expect_status=None,
            expect_status_in=_IGNORADO,
        )

    return (
        AnswerSuite(
            ref=f"mass-assignment/answer/role-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor do campo perfil",
            accepted=(r.perfil_comum, f'"{r.perfil_comum}"'),
            success_feedback="Isso. A API mostra campos que a tela não deixa editar, como o perfil.",
            failure_feedback="Ainda não. Abra /api/perfil na barra de endereço e procure a chave perfil no JSON.",
        ),
        AnswerSuite(
            ref=f"mass-assignment/answer/business-value-{r.ramo}-v1",
            version="1.0.0",
            prompt=f"Valor de {r.campo} com o maior benefício",
            accepted=(r.valor_ataque, f'"{r.valor_ataque}"'),
            success_feedback="Exato. Agora você sabe o nome do campo e o valor que quer gravar.",
            failure_feedback="Não é esse. Procure o dicionário DESCRICOES no topo de services/perfil_service.py.",
        ),
        AnswerSuite(
            ref=f"mass-assignment/answer/business-benefit-{r.ramo}-v1",
            version="1.0.0",
            prompt="Novo benefício mostrado em Meu perfil",
            accepted=r.beneficio,
            success_feedback="O PATCH gravou um campo que a tela nunca envia. Agora vamos atrás do perfil de acesso.",
            failure_feedback="Ainda não. Rode os dois comandos, recarregue Meu perfil e leia o valor na descrição.",
        ),
        AnswerSuite(
            ref=f"mass-assignment/answer/privileged-key-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor mostrado na área interna",
            accepted=(r.chave_priv,),
            success_feedback="Elevação de privilégio com um campo a mais no JSON. Agora vamos corrigir.",
            failure_feedback="Não é esse. Depois do PATCH com perfil, recarregue a aplicação e abra a área interna.",
        ),
        HttpSuite(
            ref=f"mass-assignment/python-flask/allowlist-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="comum", path="/login", form={"login": r.login[0], "senha": r.login[1]}),),
            checks=(
                HttpCheck(
                    id="contato-editavel",
                    description="A edição legítima de e-mail e telefone continua funcionando.",
                    path="/api/perfil",
                    method="PATCH",
                    as_user="comum",
                    json={"email": "validacao@exemplo.example", "telefone": "+55 11 90000-1234"},
                    contains=("90000-1234", "validacao@exemplo.example"),
                ),
                HttpCheck(
                    id="contato-salvo",
                    description="O novo telefone fica gravado e aparece em Meu perfil.",
                    path="/perfil",
                    as_user="comum",
                    contains=("90000-1234",),
                ),
                patch(
                    "perfil-recusado",
                    "Um PATCH com o campo perfil não causa erro no servidor.",
                    {"perfil": r.perfil_priv},
                ),
                HttpCheck(
                    id="perfil-mantido",
                    description="O perfil de acesso continua o original depois do PATCH com perfil.",
                    path="/api/perfil",
                    as_user="comum",
                    contains=(json_tem("perfil", r.perfil_comum),),
                ),
                HttpCheck(
                    id="area-restrita",
                    description="A área interna continua proibida ao usuário comum (403).",
                    path=f"/{r.rota_priv}",
                    as_user="comum",
                    expect_status=403,
                ),
                patch(
                    "misto-recusado",
                    f"Um PATCH que mistura telefone com {r.campo} não causa erro no servidor.",
                    {"telefone": "+55 11 90000-5678", r.campo: r.valor_ataque},
                ),
                HttpCheck(
                    id="negocio-mantido",
                    description=f"O campo {r.campo} continua com o valor original.",
                    path="/api/perfil",
                    as_user="comum",
                    contains=(json_tem(r.campo, r.valor_original),),
                ),
                patch(
                    "login-recusado",
                    "Um PATCH com o campo login não causa erro no servidor.",
                    {"login": "validacao.invasor"},
                ),
                HttpCheck(
                    id="login-mantido",
                    description="Uma lista de bloqueio não basta: o login também continua o original.",
                    path="/api/perfil",
                    as_user="comum",
                    contains=(json_tem("login", r.login[0]),),
                    not_contains=("validacao.invasor",),
                ),
            ),
            success_feedback=(
                "Correção validada numa cópia isolada do seu workspace: a API só grava e-mail e telefone, "
                "e os outros campos são ignorados ou recusados."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste o serviço e valide de novo."
            ),
        ),
    )


# --------------------------------------------------------------------------------------------------
# A2 CSRF (LAB-011 a LAB-013)


@dataclass(frozen=True, slots=True)
class CsrfRamo:
    ramo: str
    rota: str
    campo: str
    login_a: tuple[str, str]  # vítima (fictícia)
    login_b: tuple[str, str]  # outra conta, para testar token de outra sessão
    valor_ataque: str
    valor_validacao: str  # valor legítimo que a suíte grava com o token certo


CSRF_RAMOS = (
    CsrfRamo(
        "fin",
        "conta-indenizacao",
        "chave_pix",
        ("carolina.reis", "Carolina@2026"),
        ("andre.matos", "Andre@2026"),
        "recebimentos@seguro-agil.example",
        "validacao.csrf@email.example",
    ),
    CsrfRamo(
        "sau",
        "laudos/envio",
        "email_laudos",
        ("beatriz.lima", "Beatriz@2026"),
        ("joao.pedro", "JoaoP@2026"),
        "arquivo.laudos@caixa-segura.example",
        "validacao.csrf@email.example",
    ),
    CsrfRamo(
        "ind",
        "alarmes/plantao",
        "celular_plantao",
        ("leandro.vieira", "Leandro@2026"),
        ("silvana.couto", "Silvana@2026"),
        "+5511900006666",
        "+5551911112222",
    ),
)

_TOKEN_RE = r'name="csrf_token"\s+value="([^"]+)"'  # noqa: S105 - regex do campo do formulário, não um segredo
_RECUSADO = (400, 403)


def _csrf(r: CsrfRamo) -> tuple[Suite, ...]:
    pagina = f"/{r.rota}"

    def login(nome: str, cred: tuple[str, str]) -> HttpLogin:
        return HttpLogin(name=nome, path="/login", form={"login": cred[0], "senha": cred[1]})

    def nao_gravou(check_id: str, descricao: str) -> HttpCheck:
        return HttpCheck(
            id=check_id, description=descricao, path=pagina, as_user="vitima", not_contains=(r.valor_ataque,)
        )

    return (
        AnswerSuite(
            ref=f"csrf/answer/field-name-{r.ramo}-v1",
            version="1.0.0",
            prompt="Nome do campo do formulário",
            accepted=(r.campo, f'"{r.campo}"', f'name="{r.campo}"'),
            success_feedback="Isso. O POST leva só esse campo e o cookie de sessão: nada mais prova que foi você.",
            failure_feedback="Ainda não. No template, procure o atributo name do único input de texto do form.",
        ),
        AnswerSuite(
            ref=f"csrf/answer/samesite-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor do SameSite do cookie de sessão",
            accepted=("Lax", '"Lax"'),
            success_feedback="Isso. Agora veja se o Lax segura um ataque vindo do mesmo site.",
            failure_feedback="Não é esse. Abra config.py e leia o valor de SESSION_COOKIE_SAMESITE.",
        ),
        AnswerSuite(
            ref=f"csrf/answer/forged-value-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor gravado pelo ataque",
            accepted=(r.valor_ataque,),
            success_feedback="A página do atacante alterou seu cadastro sem você clicar em Salvar.",
            failure_feedback="Ainda não. Abra o site do atacante, espere a barra completar e recarregue a aplicação.",
        ),
        AnswerSuite(
            ref=f"csrf/answer/fetch-site-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor de origem no log do ataque",
            accepted=("same-site", "origem=same-site"),
            success_feedback="Exato: mesmo site, outra origem. Por isso o SameSite=Lax não barrou o cookie.",
            failure_feedback="Não é esse. Use a linha do log com o valor gravado pelo atacante, não a sua.",
        ),
        HttpSuite(
            ref=f"csrf/python-flask/synchronizer-token-{r.ramo}-v1",
            version="1.0.0",
            logins=(login("vitima", r.login_a), login("outra", r.login_b)),
            checks=(
                HttpCheck(
                    id="formulario-com-token",
                    description="O formulário traz um campo escondido csrf_token com o token da sessão.",
                    path=pagina,
                    as_user="vitima",
                    capture={"token_vitima": _TOKEN_RE},
                ),
                HttpCheck(
                    id="sem-token-recusado",
                    description="Um POST sem o token, como o da página do atacante, é recusado (400 ou 403).",
                    path=pagina,
                    method="POST",
                    as_user="vitima",
                    form={r.campo: r.valor_ataque},
                    expect_status=None,
                    expect_status_in=_RECUSADO,
                ),
                nao_gravou("sem-token-nao-gravou", "O POST sem token não alterou o cadastro."),
                HttpCheck(
                    id="token-outra-conta",
                    description="Outra conta também recebe um token no formulário.",
                    path=pagina,
                    as_user="outra",
                    capture={"token_outra": _TOKEN_RE},
                ),
                HttpCheck(
                    id="token-de-outra-sessao-recusado",
                    description="O token de outra sessão é recusado: um valor fixo no código não serve.",
                    path=pagina,
                    method="POST",
                    as_user="vitima",
                    form={r.campo: r.valor_ataque, "csrf_token": "{{token_outra}}"},
                    expect_status=None,
                    expect_status_in=_RECUSADO,
                ),
                nao_gravou(
                    "outra-sessao-nao-gravou", "O POST com token de outra sessão não alterou o cadastro."
                ),
                HttpCheck(
                    id="alteracao-legitima",
                    description="A alteração pelo próprio formulário, com o token certo, continua funcionando.",
                    path=pagina,
                    method="POST",
                    as_user="vitima",
                    form={r.campo: r.valor_validacao, "csrf_token": "{{token_vitima}}"},
                    contains=(r.valor_validacao,),
                ),
            ),
            success_feedback=(
                "Correção validada numa cópia isolada do seu workspace: só o formulário da própria aplicação, "
                "com o token da sessão, consegue alterar o cadastro."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste o controller ou o template e "
                "valide de novo."
            ),
        ),
    )


# --------------------------------------------------------------------------------------------------
# A4 senha: armazenamento inseguro de senha (LAB-017 a LAB-019)

_HASH_FORTE = r"(scrypt|pbkdf2):.+"  # formato do werkzeug, com sal e custo embutidos
_MD5_PURO = r"^[0-9a-f]{32}$"  # resumo legado (MD5), que não pode sobrar nas contas que logaram
_HASH_PADRAO = "49c572f76b3c1d9172fe2a6b75f06cf0"  # md5("Trocar@123"), igual em todos os ramos


@dataclass(frozen=True, slots=True)
class SenhaRamo:
    ramo: str
    banco: str  # nome do arquivo em /tmp/<banco>.db
    login_a: str
    senha_a: str
    nome_a: str
    login_b: str
    senha_b: str
    hash_repetido: str  # md5 da senha compartilhada por duas contas (etapa "sem-sal")


SENHA_RAMOS = (
    SenhaRamo(
        "fin",
        "credimova",
        "marina.gomes",
        "Marina#Cred26",
        "Marina Aguiar Gomes",
        "rodrigo.sena",
        "Rodrigo#Cred26",
        "c8adf383bd545d654573301c5dc2dcac",
    ),
    SenhaRamo(
        "sau",
        "helios",
        "rafael.antunes",
        "Rafael#Helios26",
        "Rafael Antunes Barreto",
        "carla.menezes",
        "Carla#Helios26",
        "de2f270e4dd8cb84d56af14073f34d7c",
    ),
    SenhaRamo(
        "ind",
        "pindorama",
        "diego.farias",
        "Diego#Pindorama26",
        "Diego Farias Lobo",
        "tania.rocha",
        "Tania#Pindorama26",
        "2d2c46d6061df0dbe5786bea484f8e66",
    ),
)


def _senha(r: SenhaRamo) -> tuple[Suite, ...]:
    db = f"/tmp/{r.banco}.db"  # noqa: S108 - caminho do banco da cópia efêmera do lab (ADR-008)
    # Logins são constantes fixas deste registro (não entrada do aluno); consulta read-only na cópia.
    consulta = f"SELECT login, senha_hash FROM usuarios WHERE login IN ('{r.login_a}', '{r.login_b}')"  # noqa: S608

    def login(nome: str, usuario: str, senha: str) -> HttpLogin:
        return HttpLogin(name=nome, path="/login", form={"login": usuario, "senha": senha})

    return (
        AnswerSuite(
            ref=f"senha/answer/hash-algo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Algoritmo usado para resumir a senha",
            accepted=("md5", "hashlib.md5", "MD5"),
            success_feedback="Isso. O MD5 é o resumo herdado do sistema legado: rápido e sem sal.",
            failure_feedback="Ainda não. Em services/auth_service.py, veja o que vem depois de hashlib. no método _resumo.",
        ),
        AnswerSuite(
            ref=f"senha/answer/hash-repetido-{r.ramo}-v1",
            version="1.0.0",
            prompt="Hash que aparece repetido no banco",
            accepted=(r.hash_repetido,),
            success_feedback="Exato: duas contas com a mesma senha têm o mesmo hash. É o que o sal evitaria.",
            failure_feedback="Não é esse. Procure o senha_hash que aparece idêntico em duas linhas.",
        ),
        AnswerSuite(
            ref=f"senha/answer/hash-default-{r.ramo}-v1",
            version="1.0.0",
            prompt="MD5 da senha padrão do legado",
            accepted=(_HASH_PADRAO,),
            success_feedback="Isso. O MD5 da senha conhecida bate com o do banco: é MD5 puro, reversível por tabela.",
            failure_feedback="Não é esse. Rode o comando python com hashlib.md5 e copie o resumo impresso.",
        ),
        AnswerSuite(
            ref=f"senha/answer/funcao-werkzeug-{r.ramo}-v1",
            version="1.0.0",
            prompt="Função do werkzeug que gera o hash forte",
            accepted=("generate_password_hash", "generate_password_hash()"),
            success_feedback="Isso. generate_password_hash gera o resumo forte, já com sal e custo.",
            failure_feedback="Ainda não. É a função que gera (não a que confere) o hash: começa com generate_.",
        ),
        HttpSuite(
            ref=f"senha/python-flask/password-hashing-{r.ramo}-v1",
            version="1.0.0",
            logins=(login("a", r.login_a, r.senha_a), login("b", r.login_b, r.senha_b)),
            checks=(
                HttpCheck(
                    id="login-legitimo",
                    description="O login legítimo continua funcionando depois da correção.",
                    path="/painel",
                    as_user="a",
                    contains=(r.nome_a,),
                ),
                HttpCheck(
                    id="senha-errada-recusada",
                    description="Uma senha errada continua sendo recusada.",
                    path="/login",
                    method="POST",
                    form={"login": r.login_a, "senha": f"{r.senha_a}-errada"},
                    contains=("inválidos",),
                    not_contains=(r.nome_a,),
                ),
            ),
            inspections=(
                InspectCheck(
                    id="hashes-migrados",
                    description=(
                        "As contas que fizeram login passaram para o formato forte (werkzeug), "
                        "nenhuma continua em MD5, e o hash confere com a senha conhecida."
                    ),
                    db_path=db,
                    query=consulta,
                    min_rows=2,
                    all_match=_HASH_FORTE,
                    none_match=_MD5_PURO,
                    verify_passwords={r.login_a: r.senha_a, r.login_b: r.senha_b},
                ),
            ),
            success_feedback=(
                "Correção validada numa cópia isolada do seu workspace: as senhas passaram para o formato "
                "forte (com sal e custo) e o login legítimo continua funcionando."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/auth_service.py e "
                "valide de novo."
            ),
        ),
    )


# --------------------------------------------------------------------------------------------------
# A3 upload: upload irrestrito levando a XSS armazenado (LAB-014 a LAB-016)

_PDF_DEMO = "%PDF-1.4\n%demonstracao\n1 0 obj\n<< >>\nendobj\n"  # PDF mínimo (assinatura %PDF)
_HTML_FORJADO = "<!doctype html><title>comprovante</title><p>x</p>"  # começa com '<', nenhuma assinatura


@dataclass(frozen=True, slots=True)
class UploadRamo:
    ramo: str
    banco: str
    rota: str
    login_a: str
    senha_a: str
    msg_recebido: str  # trecho do flash de "recebido", confirma o envio aceito
    anexo: str  # nome do anexo semeado, usado para checar o nosniff no download


UPLOAD_RAMOS = (
    UploadRamo(
        "fin",
        "credimova",
        "comprovantes",
        "marcos.nunes",
        "Marcos#Cred26",
        "Comprovante recebido",
        "comprovante-exemplo.pdf",
    ),
    UploadRamo(
        "sau",
        "sampaio",
        "pedidos",
        "carla.ribeiro",
        "Carla#Sampaio26",
        "Pedido médico recebido",
        "pedido-exemplo.pdf",
    ),
    UploadRamo(
        "ind",
        "pindorama",
        "notas",
        "fornecedor.aco",
        "Fornec#Pind26",
        "Nota fiscal recebida",
        "nota-exemplo.pdf",
    ),
)


def _upload(r: UploadRamo) -> tuple[Suite, ...]:
    rota = f"/{r.rota}"
    db = f"/tmp/{r.banco}.db"  # noqa: S108 - banco da cópia efêmera do lab (ADR-008)

    def envio(campo: str, filename: str, ctype: str, conteudo: str) -> dict[str, str]:
        return {"field": "arquivo", "filename": filename, "content_type": ctype, "content": conteudo}

    return (
        AnswerSuite(
            ref=f"upload/answer/campo-checado-{r.ramo}-v1",
            version="1.0.0",
            prompt="Atributo do arquivo que o serviço confere",
            accepted=("mimetype", "arquivo.mimetype", "content-type", "content_type", "Content-Type"),
            success_feedback="Isso. O serviço confia no tipo que o navegador informa, não no conteúdo.",
            failure_feedback="Ainda não. Em services/anexo_service.py, veja o atributo na checagem de TIPOS_PERMITIDOS.",
        ),
        AnswerSuite(
            ref=f"upload/answer/caminho-servido-{r.ramo}-v1",
            version="1.0.0",
            prompt="Caminho em que o arquivo forjado é servido",
            accepted=("/anexos/comprovante.html", "anexos/comprovante.html", "comprovante.html"),
            success_feedback="Isso. O arquivo foi guardado com o nome original e é servido em /anexos/.",
            failure_feedback="Não é esse. Clique no arquivo na lista e veja o endereço que abre.",
        ),
        AnswerSuite(
            ref=f"upload/answer/tipo-servido-{r.ramo}-v1",
            version="1.0.0",
            prompt="Content-Type com que o arquivo é servido",
            accepted=("text/html", "text/html; charset=utf-8"),
            success_feedback="Exato: servido como text/html, o navegador executa o arquivo como página.",
            failure_feedback="Não é esse. Rode o curl -I e leia a linha content-type (só o tipo, antes do ';').",
        ),
        AnswerSuite(
            ref=f"upload/answer/assinatura-pdf-{r.ramo}-v1",
            version="1.0.0",
            prompt="Assinatura com que um PDF começa",
            accepted=("%PDF", "%PDF-", "25 50 44 46"),
            success_feedback="Isso. Validar pela assinatura olha o conteúdo real, não o rótulo do cliente.",
            failure_feedback="Ainda não. Veja o começo do documento.pdf com head -c 16; são quatro caracteres.",
        ),
        HttpSuite(
            ref=f"upload/python-flask/file-upload-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="u", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="pdf-legitimo-aceito",
                    description="Um PDF de verdade continua sendo aceito depois da correção.",
                    path=rota,
                    method="POST",
                    as_user="u",
                    form={"descricao": "Documento de teste"},
                    multipart=envio("arquivo", "documento.pdf", "application/pdf", _PDF_DEMO),
                    contains=(r.msg_recebido,),
                ),
                HttpCheck(
                    id="html-forjado-recusado",
                    description="Um HTML disfarçado de imagem é recusado (o conteúdo não é PDF/PNG/JPEG).",
                    path=rota,
                    method="POST",
                    as_user="u",
                    form={"descricao": "Comprovante"},
                    multipart=envio("arquivo", "comprovante.html", "image/png", _HTML_FORJADO),
                    expect_status=None,
                    expect_status_in=(400,),
                ),
                HttpCheck(
                    id="download-sem-sniff",
                    description="O download manda o navegador não adivinhar o tipo (X-Content-Type-Options: nosniff).",
                    path=f"/anexos/{r.anexo}",
                    as_user="u",
                    expect_headers={"X-Content-Type-Options": "nosniff"},
                ),
            ),
            inspections=(
                InspectCheck(
                    id="sem-html-armazenado",
                    description="Nenhum anexo guardado termina em .html: o HTML forjado foi recusado, não gravado.",
                    db_path=db,
                    query="SELECT id, nome_arquivo FROM anexos",
                    min_rows=1,
                    none_match=r"\.html$",
                ),
            ),
            success_feedback=(
                "Correção validada numa cópia isolada do seu workspace: um PDF de verdade é aceito, o HTML "
                "forjado é recusado, nada é guardado como .html e o download vem com nosniff."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste o serviço ou o controller e "
                "valide de novo."
            ),
        ),
    )


# --------------------------------------------------------------------------------------------------
# A6 ssrf: Server-Side Request Forgery no importador por URL (LAB-020 a LAB-022)


@dataclass(frozen=True, slots=True)
class SsrfRamo:
    ramo: str
    login_a: str
    senha_a: str
    doc_trecho: str  # trecho do documento legítimo; confirma que a busca permitida continua funcionando
    meta_chave: str  # credencial fictícia que o console interno vaza; não pode voltar depois da correção


SSRF_RAMOS = (
    SsrfRamo(
        "fin",
        "analista.credito",
        "Analista#Cred26",
        "Renda bruta mensal",
        "CHAVE-FICTICIA-CREDIMOVA-NAO-USAR",
    ),
    SsrfRamo(
        "sau",
        "recepcao.laudos",
        "Recepcao#Sampaio26",
        "Hemograma completo",
        "CHAVE-FICTICIA-SAMPAIO-NAO-USAR",
    ),
    SsrfRamo(
        "ind",
        "eng.processos",
        "Engenharia#Pind26",
        "Chapa de aço laminado",
        "CHAVE-FICTICIA-PINDORAMA-NAO-USAR",
    ),
)

_DOC_LEGITIMO = "http://127.0.0.1:8090/doc/1"  # Serviço de Documentos interno (destino permitido)
_CONSOLE_INTERNO = "http://127.0.0.1:9000/infra/credenciais"  # Console de Infraestrutura (uso interno)


def _ssrf(r: SsrfRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"ssrf/answer/funcao-busca-{r.ramo}-v1",
            version="1.0.0",
            prompt="Função que abre a URL no servidor",
            accepted=("urlopen", "urllib.request.urlopen", "request.urlopen", "urlopen()"),
            success_feedback="Isso. urlopen abre, no servidor, a URL que veio do formulário.",
            failure_feedback="Ainda não. Em services/importador_service.py, veja o que vem depois de urllib.request.",
        ),
        AnswerSuite(
            ref=f"ssrf/answer/credencial-vazada-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor do campo chave_integracao vazado pelo console interno",
            accepted=(r.meta_chave,),
            success_feedback="Exato: pela tela de importar você leu um segredo de infraestrutura. Isso é SSRF.",
            failure_feedback="Não é esse. Busque a URL do console interno e copie o campo chave_integracao do JSON.",
        ),
        AnswerSuite(
            ref=f"ssrf/answer/destino-legitimo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Host e porta do único destino legítimo",
            accepted=("127.0.0.1:8090", "http://127.0.0.1:8090", "127.0.0.1:8090/"),
            success_feedback="Isso. O importador só precisa do Serviço de Documentos; o resto deve ser recusado.",
            failure_feedback="Não é esse. É o host:porta da URL http://____/doc/1 que você buscou na etapa 1.",
        ),
        AnswerSuite(
            ref=f"ssrf/answer/defesa-{r.ramo}-v1",
            version="1.0.0",
            prompt="Defesa que lista o que é permitido e recusa o resto",
            accepted=(
                "allowlist",
                "allow-list",
                "allow list",
                "lista de permissão",
                "lista de permissao",
                "lista de permissões",
                "lista de permissoes",
            ),
            success_feedback="Isso. A allowlist descreve o que é aceito e recusa todo o resto.",
            failure_feedback="Ainda não. É o oposto de blocklist: em português, lista de permissão.",
        ),
        HttpSuite(
            ref=f"ssrf/python-flask/importador-allowlist-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="a", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="documento-legitimo",
                    description="A busca do documento legítimo (Serviço de Documentos) continua funcionando.",
                    path="/importar",
                    method="POST",
                    as_user="a",
                    form={"url": _DOC_LEGITIMO},
                    contains=(r.doc_trecho,),
                ),
                HttpCheck(
                    id="console-interno-bloqueado",
                    description="A busca do console interno é recusada e a credencial não volta mais.",
                    path="/importar",
                    method="POST",
                    as_user="a",
                    form={"url": _CONSOLE_INTERNO},
                    contains=("não permitido",),
                    not_contains=(r.meta_chave,),
                ),
                HttpCheck(
                    id="esquema-arquivo-bloqueado",
                    description="Um destino file:// (fora da lista de permissão) também é recusado.",
                    path="/importar",
                    method="POST",
                    as_user="a",
                    form={"url": "file:///etc/hostname"},
                    contains=("não permitido",),
                ),
            ),
            success_feedback=(
                "Correção validada: o documento legítimo continua sendo buscado e o console interno "
                "(e outros destinos) é recusado — o servidor não busca mais qualquer URL."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/importador_service.py "
                "e valide de novo."
            ),
        ),
    )


# --------------------------------------------------------------------------------------------------
# A8 logica-negocio: falha de lógica de negócio no resgate (LAB-023 a LAB-025)


@dataclass(frozen=True, slots=True)
class LogicaRamo:
    ramo: str
    login_a: str
    senha_a: str


LOGICA_RAMOS = (
    LogicaRamo("fin", "marina.gomes", "Marina#Cred26"),
    LogicaRamo("sau", "rafael.antunes", "Rafael#Sereno26"),
    LogicaRamo("ind", "diego.farias", "Diego#Voltera26"),
)


def _logica(r: LogicaRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"logica-negocio/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que executa o resgate",
            accepted=("resgatar", "resgatar()"),
            success_feedback="Isso. É em resgatar que a regra de negócio deveria valer.",
            failure_feedback="Ainda não. Em services/resgate_service.py, veja o único método público da classe.",
        ),
        AnswerSuite(
            ref=f"logica-negocio/answer/aceito-{r.ramo}-v1",
            version="1.0.0",
            prompt="O resgate acima do saldo foi aceito ou recusado?",
            accepted=("aceito", "aceita", "foi aceito"),
            success_feedback="Exato: sem validação, o servidor aceitou um resgate acima do saldo.",
            failure_feedback="Não é isso. Veja a mensagem depois de resgatar 999999: a operação foi registrada.",
        ),
        AnswerSuite(
            ref=f"logica-negocio/answer/limite-{r.ramo}-v1",
            version="1.0.0",
            prompt="O valor do resgate não pode passar do quê",
            accepted=("saldo", "saldo disponível", "saldo disponivel", "o saldo", "do saldo"),
            success_feedback="Isso. O valor não pode passar do saldo disponível.",
            failure_feedback="Ainda não. É o quanto você tem disponível, mostrado no painel.",
        ),
        AnswerSuite(
            ref=f"logica-negocio/answer/onde-{r.ramo}-v1",
            version="1.0.0",
            prompt="Onde a regra de negócio tem que ser conferida",
            accepted=(
                "servidor",
                "no servidor",
                "lado do servidor",
                "no lado do servidor",
                "backend",
                "no backend",
                "server-side",
                "server side",
            ),
            success_feedback="Isso. A regra que vale é a que roda no servidor, não no navegador.",
            failure_feedback="Ainda não. O atacante não usa o seu formulário; a checagem tem que valer do outro lado.",
        ),
        HttpSuite(
            ref=f"logica-negocio/python-flask/resgate-validado-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="a", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="resgate-legitimo",
                    description="Um resgate dentro do saldo continua funcionando depois da correção.",
                    path="/resgatar",
                    method="POST",
                    as_user="a",
                    form={"valor": "100"},
                    contains=("Operação registrada",),
                ),
                HttpCheck(
                    id="acima-do-saldo-recusado",
                    description="Um resgate acima do saldo é recusado.",
                    path="/resgatar",
                    method="POST",
                    as_user="a",
                    form={"valor": "999999"},
                    contains=("acima do saldo",),
                    not_contains=("Operação registrada",),
                ),
                HttpCheck(
                    id="valor-negativo-recusado",
                    description="Um valor negativo é recusado (não credita o usuário).",
                    path="/resgatar",
                    method="POST",
                    as_user="a",
                    form={"valor": "-50"},
                    contains=("deve ser positivo",),
                    not_contains=("Operação registrada",),
                ),
            ),
            success_feedback=(
                "Correção validada: o resgate legítimo funciona, e valores acima do saldo ou negativos "
                "são recusados — a regra de negócio agora vale no servidor."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/resgate_service.py "
                "e valide de novo."
            ),
        ),
    )


# A13 tentativas-login: login sem limite de tentativas / força bruta (LAB-026 a LAB-028)


@dataclass(frozen=True, slots=True)
class TentativasRamo:
    ramo: str
    login_a: str  # alvo da força bruta (senhas erradas)
    login_b: str  # conta legítima, não bloqueada, para provar que o login normal segue funcionando
    senha_b: str


TENTATIVAS_RAMOS = (
    TentativasRamo("fin", "ana.ribeiro", "carlos.moura", "Carlos#Pagomais26"),
    TentativasRamo("sau", "marcos.tavares", "renata.borges", "Renata#Lumen26"),
    TentativasRamo("ind", "diego.campos", "sonia.barros", "Sonia#Aurora26"),
)


def _tentativas(r: TentativasRamo) -> tuple[Suite, ...]:
    # Cinco tentativas erradas seguidas para o mesmo usuário, depois a sexta (que deve bloquear após
    # a correção). O contador vive no servidor por usuário, então cada requisição anônima acumula.
    erros = tuple(
        HttpCheck(
            id=f"erro-{n}",
            description=f"Tentativa {n} com senha errada é recusada como credencial inválida.",
            path="/login",
            method="POST",
            form={"login": r.login_a, "senha": f"errada{n}"},
            contains=("inválid",),
            not_contains=("Muitas tentativas",),
        )
        for n in range(1, 6)
    )
    return (
        AnswerSuite(
            ref=f"tentativas-login/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que confere o login e a senha",
            accepted=("autenticar", "autenticar()"),
            success_feedback="Isso. É em autenticar que deveria haver um limite de tentativas.",
            failure_feedback="Ainda não. Em services/auth_service.py, veja o único método público da classe.",
        ),
        AnswerSuite(
            ref=f"tentativas-login/answer/comportamento-{r.ramo}-v1",
            version="1.0.0",
            prompt="Depois de muitas tentativas erradas, o login bloqueia ou continua aceitando?",
            accepted=(
                "continua",
                "continua aceitando",
                "continua aceitando tentativas",
                "continuou",
                "aceita",
                "aceitando",
                "não bloqueia",
                "nao bloqueia",
            ),
            success_feedback="Exato: sem limite, o login continua aceitando tentativas para sempre.",
            failure_feedback="Não é isso. Por mais que você erre, a mensagem é a mesma e o login nunca trava.",
        ),
        AnswerSuite(
            ref=f"tentativas-login/answer/defesa-{r.ramo}-v1",
            version="1.0.0",
            prompt="O login precisa limitar o número de quê por usuário",
            accepted=(
                "tentativas",
                "tentativas de login",
                "as tentativas",
                "tentativa",
                "número de tentativas",
                "numero de tentativas",
            ),
            success_feedback="Isso. A defesa é limitar as tentativas de login por usuário.",
            failure_feedback="Ainda não. É o que o atacante faz muitas vezes seguidas até acertar a senha.",
        ),
        AnswerSuite(
            ref=f"tentativas-login/answer/onde-{r.ramo}-v1",
            version="1.0.0",
            prompt="Onde o limite de tentativas tem que ser contado e aplicado",
            accepted=(
                "servidor",
                "no servidor",
                "lado do servidor",
                "no lado do servidor",
                "backend",
                "no backend",
                "server-side",
                "server side",
            ),
            success_feedback="Isso. O limite que vale é o que o servidor conta e aplica, não o navegador.",
            failure_feedback="Ainda não. O atacante não usa a sua tela; a contagem tem que valer do outro lado.",
        ),
        HttpSuite(
            ref=f"tentativas-login/python-flask/login-protegido-{r.ramo}-v1",
            version="1.0.0",
            checks=(
                *erros,
                HttpCheck(
                    id="bloqueio-apos-limite",
                    description="Depois do limite de tentativas, uma nova tentativa é bloqueada.",
                    path="/login",
                    method="POST",
                    form={"login": r.login_a, "senha": "errada6"},
                    contains=("Muitas tentativas",),
                ),
                HttpCheck(
                    id="login-legitimo",
                    description="Um usuário diferente, não bloqueado, continua conseguindo entrar.",
                    path="/login",
                    method="POST",
                    form={"login": r.login_b, "senha": r.senha_b},
                    contains=("Sair",),
                    not_contains=("inválid", "Muitas tentativas"),
                ),
            ),
            success_feedback=(
                "Correção validada: o login bloqueia após o limite de tentativas, e um usuário diferente "
                "continua entrando — o limite agora vale por usuário, no servidor."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/auth_service.py "
                "e valide de novo. O limite deve ser por usuário (não global) e contado no servidor."
            ),
        ),
    )


# A7 cors: CORS mal configurado que reflete qualquer origem (LAB-029 a LAB-031)

CORS_ORIGEM_CONFIAVEL = "https://portal.exemplo"
CORS_ORIGEM_MALICIOSA = "https://malicioso.example"


@dataclass(frozen=True, slots=True)
class CorsRamo:
    ramo: str
    login_a: str
    senha_a: str


CORS_RAMOS = (
    CorsRamo("fin", "lucas.andrade", "Lucas#Montara26"),
    CorsRamo("sau", "fernanda.lopes", "Fernanda#Vitalis26"),
    CorsRamo("ind", "marcelo.dantas", "Marcelo#Corrente26"),
)


def _cors(r: CorsRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"cors/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que monta os cabeçalhos de CORS",
            accepted=("cabecalhos", "cabeçalhos", "cabecalhos()", "cabeçalhos()"),
            success_feedback="Isso. É em cabecalhos que se decide qual origem é liberada.",
            failure_feedback="Ainda não. Em services/cors_service.py, veja o único método público da classe.",
        ),
        AnswerSuite(
            ref=f"cors/answer/reflete-{r.ramo}-v1",
            version="1.0.0",
            prompt="A API reflete (devolve) a origem recebida ou a recusa?",
            accepted=("reflete", "reflete a origem", "devolve", "devolve a origem", "espelha"),
            success_feedback="Exato: a API devolve de volta a mesma origem que recebeu, seja qual for.",
            failure_feedback="Não é isso. Compare a origem que você enviou no curl com a que voltou no cabeçalho.",
        ),
        AnswerSuite(
            ref=f"cors/answer/defesa-{r.ramo}-v1",
            version="1.0.0",
            prompt="As origens confiáveis devem ficar guardadas numa o quê",
            accepted=(
                "lista",
                "lista de permissão",
                "lista de origens",
                "lista de origens confiáveis",
                "allowlist",
                "uma lista",
            ),
            success_feedback="Isso. A defesa é uma lista de origens confiáveis (allowlist).",
            failure_feedback="Ainda não. É uma relação fixa das origens que podem ler a API.",
        ),
        AnswerSuite(
            ref=f"cors/answer/credenciais-{r.ramo}-v1",
            version="1.0.0",
            prompt="O que o Allow-Credentials libera, além da origem",
            accepted=(
                "credenciais",
                "credencial",
                "as credenciais",
                "cookie",
                "cookies",
                "cookie de sessão",
                "o cookie",
            ),
            success_feedback="Isso. Allow-Credentials libera o uso das credenciais (o cookie de sessão) da vítima.",
            failure_feedback="Ainda não. É o que o fetch envia com credentials: 'include' — o cookie da sessão.",
        ),
        HttpSuite(
            ref=f"cors/python-flask/cors-restrito-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="a", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="perfil-dados",
                    description="A API de perfil continua devolvendo os dados do usuário logado.",
                    path="/api/perfil",
                    as_user="a",
                    contains=(r.login_a,),
                ),
                HttpCheck(
                    id="origem-maliciosa-sem-reflexo",
                    description="Uma origem não confiável não é refletida no Access-Control-Allow-Origin.",
                    path="/api/perfil",
                    as_user="a",
                    headers={"Origin": CORS_ORIGEM_MALICIOSA},
                    expect_absent_headers={"Access-Control-Allow-Origin": "malicioso"},
                ),
                HttpCheck(
                    id="credenciais-nao-liberadas",
                    description="Para origem não confiável, não se libera o envio de credenciais.",
                    path="/api/perfil",
                    as_user="a",
                    headers={"Origin": CORS_ORIGEM_MALICIOSA},
                    expect_absent_headers={"Access-Control-Allow-Credentials": "true"},
                ),
                HttpCheck(
                    id="origem-confiavel-liberada",
                    description="Uma origem confiável continua liberada no CORS.",
                    path="/api/perfil",
                    as_user="a",
                    headers={"Origin": CORS_ORIGEM_CONFIAVEL},
                    expect_headers={"Access-Control-Allow-Origin": "portal.exemplo"},
                ),
            ),
            success_feedback=(
                "Correção validada: a API libera no CORS só a origem confiável e deixa de refletir "
                "origens estranhas (e de liberar credenciais para elas)."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/cors_service.py "
                "e valide de novo. Libere só origens de uma lista confiável; para as demais, nenhum cabeçalho de CORS."
            ),
        ),
    )


# A12 path-traversal: download de documento sai da pasta com ../ ou caminho absoluto (LAB-032 a LAB-034)


@dataclass(frozen=True, slots=True)
class PathRamo:
    ramo: str
    login_a: str
    senha_a: str


PATH_RAMOS = (
    PathRamo("fin", "lucas.andrade", "Lucas#Montara26"),
    PathRamo("sau", "fernanda.lopes", "Fernanda#Vitalis26"),
    PathRamo("ind", "marcelo.dantas", "Marcelo#Corrente26"),
)


def _path(r: PathRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"path-traversal/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que lê o documento",
            accepted=("ler", "ler()"),
            success_feedback="Isso. É em ler que deveria haver a conferência da pasta.",
            failure_feedback="Ainda não. Em services/documento_service.py, veja o único método público da classe.",
        ),
        AnswerSuite(
            ref=f"path-traversal/answer/saiu-{r.ramo}-v1",
            version="1.0.0",
            prompt="Com ../, o download saiu da pasta de documentos ou ficou dentro dela?",
            accepted=("saiu", "saiu da pasta", "sai", "saiu fora", "fora", "escapou"),
            success_feedback="Exato: o ../ subiu um nível e leu um arquivo de fora da pasta de documentos.",
            failure_feedback="Não é isso. O segredo_interno.txt fica fora da pasta documentos/.",
        ),
        AnswerSuite(
            ref=f"path-traversal/answer/absoluto-{r.ramo}-v1",
            version="1.0.0",
            prompt="Que tipo de caminho ignora a pasta base mesmo sem ..",
            accepted=("absoluto", "caminho absoluto", "absolute", "path absoluto"),
            success_feedback="Isso. Um caminho absoluto aponta desde a raiz e ignora a pasta base.",
            failure_feedback="Ainda não. Começa com / e aponta o arquivo desde a raiz do sistema.",
        ),
        AnswerSuite(
            ref=f"path-traversal/answer/regra-{r.ramo}-v1",
            version="1.0.0",
            prompt="O caminho final tem que ficar onde, em relação à pasta de documentos",
            accepted=("dentro", "dentro da pasta", "dentro dela", "para dentro"),
            success_feedback="Isso. O caminho final tem que ficar dentro da pasta de documentos.",
            failure_feedback="Ainda não. É o oposto de 'fora': o caminho não pode escapar da pasta base.",
        ),
        HttpSuite(
            ref=f"path-traversal/python-flask/documento-seguro-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="a", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="documento-legitimo",
                    description="Um documento da pasta continua podendo ser baixado.",
                    path="/documento?nome=extrato.txt",
                    as_user="a",
                    contains=("DOCUMENTO-EXTRATO",),
                ),
                HttpCheck(
                    id="traversal-relativo-bloqueado",
                    description="Um nome com ../ não consegue mais ler arquivos de fora da pasta.",
                    path="/documento?nome=../segredo_interno.txt",
                    as_user="a",
                    contains=("não",),
                    not_contains=("CHAVE-INTERNA",),
                ),
                HttpCheck(
                    id="traversal-absoluto-bloqueado",
                    description="Um caminho absoluto também não consegue ler arquivos de fora da pasta.",
                    path="/documento?nome=/workspace/segredo_interno.txt",
                    as_user="a",
                    contains=("não",),
                    not_contains=("CHAVE-INTERNA",),
                ),
            ),
            success_feedback=(
                "Correção validada: o documento legítimo continua baixando, e ../ ou caminho absoluto "
                "não leem mais arquivos de fora da pasta de documentos."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste "
                "services/documento_service.py e valide de novo. Garanta que o caminho final fique dentro da base."
            ),
        ),
    )


# A10 confianca-cliente: a loja confia no custo que o cliente envia (LAB-035 a LAB-037)
# Seed fixo em todos os ramos: saldo inicial 500 pontos, produto 1 custa 300 (saldo correto após: 200).


@dataclass(frozen=True, slots=True)
class ConfiancaRamo:
    ramo: str
    login_a: str
    senha_a: str


CONFIANCA_RAMOS = (
    ConfiancaRamo("fin", "marina.gomes", "Marina#Cred26"),
    ConfiancaRamo("sau", "rafael.antunes", "Rafael#Sereno26"),
    ConfiancaRamo("ind", "diego.farias", "Diego#Voltera26"),
)


def _confianca(r: ConfiancaRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"confianca-cliente/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que resgata o produto",
            accepted=("resgatar", "resgatar()"),
            success_feedback="Isso. É em resgatar que o custo deveria vir do banco, não do formulário.",
            failure_feedback="Ainda não. Em services/loja_service.py, veja o único método público da classe.",
        ),
        AnswerSuite(
            ref=f"confianca-cliente/answer/quem-define-{r.ramo}-v1",
            version="1.0.0",
            prompt="Quem deve definir o custo do produto: o cliente ou a loja (servidor)?",
            accepted=("loja", "a loja", "servidor", "o servidor", "o banco", "banco", "backend"),
            success_feedback="Exato: o custo é um dado da loja; ele está no servidor, no banco.",
            failure_feedback="Não é isso. O custo não pode ser escolhido por quem faz o pedido.",
        ),
        AnswerSuite(
            ref=f"confianca-cliente/answer/vem-de-onde-{r.ramo}-v1",
            version="1.0.0",
            prompt="De onde o custo correto do produto deve ser lido",
            accepted=(
                "banco",
                "do banco",
                "banco de dados",
                "servidor",
                "do servidor",
                "produto",
                "do produto",
                "tabela de produtos",
            ),
            success_feedback="Isso. O custo correto vem do produto no banco, não do formulário.",
            failure_feedback="Ainda não. É onde a loja guarda o custo de cada produto.",
        ),
        AnswerSuite(
            ref=f"confianca-cliente/answer/confiar-{r.ramo}-v1",
            version="1.0.0",
            prompt="O servidor deve confiar no custo que veio do formulário? (sim/não)",
            accepted=("não", "nao", "não deve", "nao deve", "jamais", "nunca"),
            success_feedback="Isso. O servidor não confia em dado que o cliente controla e que ele mesmo pode determinar.",
            failure_feedback="Ainda não. O cliente pode mandar qualquer custo; o servidor tem o custo real.",
        ),
        HttpSuite(
            ref=f"confianca-cliente/python-flask/loja-servidor-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="a", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="catalogo-visivel",
                    description="A loja mostra o catálogo com o custo real e o saldo inicial.",
                    path="/painel",
                    as_user="a",
                    contains=("300", "500"),
                ),
                HttpCheck(
                    id="custo-real-cobrado",
                    description="Ao resgatar com um custo adulterado, a loja cobra o custo REAL do produto.",
                    path="/resgatar",
                    method="POST",
                    as_user="a",
                    form={"produto_id": "1", "custo": "1"},
                    contains=("Saldo restante: 200",),
                    not_contains=("499",),
                ),
            ),
            success_feedback=(
                "Correção validada: o resgate cobra o custo real do produto (do banco), ignorando o "
                "custo enviado no formulário."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/loja_service.py "
                "e valide de novo. O custo tem que vir do produto no banco, não do formulário."
            ),
        ),
    )


# A15 autorizacao-api: API administrativa sem conferência de papel / BFLA (LAB-038 a LAB-040)


@dataclass(frozen=True, slots=True)
class AutorizacaoRamo:
    ramo: str
    login_admin: str
    senha_admin: str
    login_a: str
    senha_a: str


AUTORIZACAO_RAMOS = (
    AutorizacaoRamo("fin", "paula.couto", "Paula#Lumina26", "joao.mendes", "Joao#Lumina26"),
    AutorizacaoRamo("sau", "sandra.rocha", "Sandra#SantaClara26", "pedro.alves", "Pedro#SantaClara26"),
    AutorizacaoRamo("ind", "claudia.reis", "Claudia#Horizonte26", "felipe.gomes", "Felipe#Horizonte26"),
)


def _autorizacao(r: AutorizacaoRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"autorizacao-api/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que decide se o papel pode usar as funções administrativas",
            accepted=("pode_administrar", "pode_administrar()"),
            success_feedback="Isso. É em pode_administrar que deveria haver a conferência do papel.",
            failure_feedback="Ainda não. Em services/permissao_service.py, veja o único método público.",
        ),
        AnswerSuite(
            ref=f"autorizacao-api/answer/resultado-{r.ramo}-v1",
            version="1.0.0",
            prompt="O usuário comum conseguiu usar a API de admin ou foi barrado?",
            accepted=("conseguiu", "consegue", "conseguiu usar", "acessou", "passou", "funcionou"),
            success_feedback="Exato: sem conferência de papel, o usuário comum chamou a API de admin.",
            failure_feedback="Não é isso. A lista de usuários voltou normalmente, mesmo para o comum.",
        ),
        AnswerSuite(
            ref=f"autorizacao-api/answer/conceito-{r.ramo}-v1",
            version="1.0.0",
            prompt="Checagem que falta: não 'quem é o usuário', mas 'o que ele pode fazer'",
            accepted=("autorização", "autorizacao", "autorização", "authorization"),
            success_feedback="Isso. Falta a autorização: decidir o que o usuário pode fazer.",
            failure_feedback="Ainda não. Começa com 'autor...' e é sobre permissão, não identidade.",
        ),
        AnswerSuite(
            ref=f"autorizacao-api/answer/papel-{r.ramo}-v1",
            version="1.0.0",
            prompt="Papel exigido para usar a API administrativa",
            accepted=("admin", "administrador", "papel admin", "administrator"),
            success_feedback="Isso. Só o papel admin pode usar a função administrativa.",
            failure_feedback="Ainda não. É o papel oposto de 'comum'.",
        ),
        HttpSuite(
            ref=f"autorizacao-api/python-flask/autorizacao-funcao-{r.ramo}-v1",
            version="1.0.0",
            logins=(
                HttpLogin(name="adm", path="/login", form={"login": r.login_admin, "senha": r.senha_admin}),
                HttpLogin(name="comum", path="/login", form={"login": r.login_a, "senha": r.senha_a}),
            ),
            checks=(
                HttpCheck(
                    id="admin-liberado",
                    description="O administrador continua conseguindo listar os usuários.",
                    path="/api/admin/usuarios",
                    as_user="adm",
                    contains=("usuarios",),
                ),
                HttpCheck(
                    id="comum-bloqueado",
                    description="O usuário comum é barrado (403) ao chamar a API administrativa.",
                    path="/api/admin/usuarios",
                    as_user="comum",
                    expect_status=403,
                    contains=("negado",),
                ),
            ),
            success_feedback=(
                "Correção validada: o administrador continua usando a API, e o usuário comum recebe "
                "acesso negado — a função agora confere o papel no servidor."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste "
                "services/permissao_service.py e valide de novo. Só o papel admin pode usar a função."
            ),
        ),
    )


# A19 erros-verbosos: a API devolve o traceback completo em erros (LAB-041 a LAB-043)


@dataclass(frozen=True, slots=True)
class ErrosRamo:
    ramo: str
    login_a: str
    senha_a: str


ERROS_RAMOS = (
    ErrosRamo("fin", "andre.luz", "Andre#Nimbo26"),
    ErrosRamo("sau", "sofia.melo", "Sofia#Prisma26"),
    ErrosRamo("ind", "rogerio.pena", "Rogerio#Delta26"),
)


def _erros(r: ErrosRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"erros-verbosos/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que monta o corpo de erro devolvido ao cliente",
            accepted=("resposta", "resposta()"),
            success_feedback="Isso. É em resposta que o detalhe do erro vaza para o cliente.",
            failure_feedback="Ainda não. Em services/erro_service.py, veja o único método público.",
        ),
        AnswerSuite(
            ref=f"erros-verbosos/answer/aparece-{r.ramo}-v1",
            version="1.0.0",
            prompt="O traceback aparece ou não aparece na resposta ao cliente?",
            accepted=("aparece", "aparece sim", "sim", "apareceu", "vaza", "vazou"),
            success_feedback="Exato: o traceback completo apareceu no corpo da resposta.",
            failure_feedback="Não é isso. Procure o campo detalhe na resposta do curl: ele traz o traceback.",
        ),
        AnswerSuite(
            ref=f"erros-verbosos/answer/onde-{r.ramo}-v1",
            version="1.0.0",
            prompt="Para onde o detalhe do erro deve ir, em vez da resposta ao cliente",
            accepted=("log", "no log", "logs", "nos logs", "log do servidor", "registro"),
            success_feedback="Isso. O detalhe vai para o log do servidor.",
            failure_feedback="Ainda não. É onde o servidor registra o que aconteceu, para a equipe ler depois.",
        ),
        AnswerSuite(
            ref=f"erros-verbosos/answer/mensagem-{r.ramo}-v1",
            version="1.0.0",
            prompt="Que tipo de mensagem o cliente deve receber no lugar do traceback",
            accepted=(
                "genérica",
                "generica",
                "mensagem genérica",
                "mensagem generica",
                "genérico",
                "generico",
            ),
            success_feedback="Isso. O cliente recebe apenas uma mensagem genérica.",
            failure_feedback="Ainda não. É o oposto de detalhada: serve para qualquer erro, sem revelar nada.",
        ),
        HttpSuite(
            ref=f"erros-verbosos/python-flask/erro-generico-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="a", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="relatorio-ok",
                    description="Um relatório com mês válido continua funcionando.",
                    path="/api/relatorio?mes=3",
                    as_user="a",
                    contains=("ok",),
                ),
                HttpCheck(
                    id="erro-sem-traceback",
                    description="Um erro responde com mensagem genérica, sem traceback nem detalhe interno.",
                    path="/api/relatorio?mes=abc",
                    as_user="a",
                    expect_status=500,
                    contains=("Erro interno",),
                    not_contains=("Traceback", "/workspace/"),
                ),
            ),
            success_feedback=(
                "Correção validada: o relatório válido funciona, e um erro responde com mensagem "
                "genérica, sem traceback nem caminhos internos (o detalhe fica no log do servidor)."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/erro_service.py "
                "e valide de novo. O cliente só pode receber uma mensagem genérica; o detalhe vai para o log."
            ),
        ),
    )


# A17 graphql-bola: resolver GraphQL que devolve o objeto sem conferir o dono / BOLA (LAB-047 a LAB-049)


@dataclass(frozen=True, slots=True)
class GraphqlRamo:
    ramo: str
    login_a: str  # dono do pedido de id 1
    senha_a: str
    trecho_proprio: str  # trecho da descrição do pedido 1 (do usuário logado)
    trecho_outro: str  # trecho da descrição do pedido 2 (de OUTRO usuário); só vaza se houver BOLA


GRAPHQL_RAMOS = (
    GraphqlRamo("fin", "ana.ribeiro", "Ana#Pagomais26", "Vale Insumos", "Norte Logistica"),
    GraphqlRamo("sau", "marcos.tavares", "Marcos#Lumen26", "hemograma completo", "ressonancia de joelho"),
    GraphqlRamo("ind", "diego.campos", "Diego#Aurora26", "bomba 4", "turbina 2"),
)


def _graphql(r: GraphqlRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"graphql-bola/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que resolve o pedido na API GraphQL",
            accepted=("resolver", "resolver()"),
            success_feedback="Isso. É em resolver que falta conferir o dono do pedido.",
            failure_feedback="Ainda não. Em services/pedido_service.py, veja o único método público da classe.",
        ),
        AnswerSuite(
            ref=f"graphql-bola/answer/comportamento-{r.ramo}-v1",
            version="1.0.0",
            prompt="Pedindo o id de outro usuário, a API devolve o pedido ou nega?",
            accepted=(
                "devolve",
                "devolve o pedido",
                "devolve o pedido de outro",
                "devolve de outro",
                "devolveu",
                "entrega",
                "retorna",
                "mostra",
            ),
            success_feedback="Exato: sem conferir o dono, a API devolve o pedido de outro usuário.",
            failure_feedback="Não é isso. Peça o id 2 logado como o dono do id 1 e veja a descrição de outro voltar.",
        ),
        AnswerSuite(
            ref=f"graphql-bola/answer/defesa-{r.ramo}-v1",
            version="1.0.0",
            prompt="O resolver precisa conferir o quê do pedido antes de devolvê-lo",
            accepted=(
                "dono",
                "o dono",
                "o dono do pedido",
                "dono do pedido",
                "proprietário",
                "proprietario",
                "o proprietário",
                "o proprietario",
                "titular",
                "o titular",
            ),
            success_feedback="Isso. O resolver precisa conferir se o dono do pedido é o usuário logado.",
            failure_feedback="Ainda não. É quem o pedido pertence (a coluna dono_id).",
        ),
        AnswerSuite(
            ref=f"graphql-bola/answer/onde-{r.ramo}-v1",
            version="1.0.0",
            prompt="Estar logado já garante, sozinho, que você só vê os seus pedidos?",
            accepted=(
                "não",
                "nao",
                "não garante",
                "nao garante",
                "não basta",
                "nao basta",
                "não, não basta",
            ),
            success_feedback="Isso. Login diz quem você é; não diz a quais objetos você tem direito.",
            failure_feedback="Ainda não. Você estava logado e mesmo assim leu o pedido de outro.",
        ),
        HttpSuite(
            ref=f"graphql-bola/python-flask/resolver-protegido-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="a", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="proprio-ok",
                    description="Pedir o próprio pedido (id 1) continua funcionando depois da correção.",
                    path="/graphql",
                    method="POST",
                    as_user="a",
                    json={"query": "{ pedido(id: 1) { descricao valor } }", "variables": {"id": 1}},
                    contains=(r.trecho_proprio,),
                ),
                HttpCheck(
                    id="de-outro-negado",
                    description="Pedir o pedido de outro usuário (id 2) é negado, sem vazar a descrição.",
                    path="/graphql",
                    method="POST",
                    as_user="a",
                    json={"query": "{ pedido(id: 2) { descricao valor } }", "variables": {"id": 2}},
                    contains=("acesso negado",),
                    not_contains=(r.trecho_outro,),
                ),
            ),
            success_feedback=(
                "Correção validada: você continua lendo o seu pedido, e o pedido de outro usuário é "
                "negado — o resolver agora confere o dono de cada objeto."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/pedido_service.py "
                "e valide de novo. O resolver deve comparar o dono do pedido com o usuário logado."
            ),
        ),
    )


# A18 ldap-injection: busca que junta o nome cru no filtro LDAP / injeção (LAB-044 a LAB-046)


@dataclass(frozen=True, slots=True)
class LdapRamo:
    ramo: str
    login_a: str  # conta de suporte que faz login (nome distinto das pessoas do diretório)
    senha_a: str
    cn_a: str  # cn exato de uma pessoa do diretório: a busca legítima acha só ela
    cn_outro: str  # cn de OUTRA pessoa, que só aparece se o * vazar o diretório inteiro


LDAP_RAMOS = (
    LdapRamo("fin", "ti.suporte", "TI#Pagomais26", "Ana Ribeiro Teixeira", "Carlos Moura Pinto"),
    LdapRamo("sau", "ti.suporte", "TI#Lumen26", "Marcos Tavares Lima", "Renata Borges Nunes"),
    LdapRamo("ind", "ti.suporte", "TI#Aurora26", "Diego Campos Ferraz", "Sonia Barros Teles"),
)


def _ldap(r: LdapRamo) -> tuple[Suite, ...]:
    busca_legitima = f"/buscar?nome={urllib.parse.quote(r.cn_a)}"
    busca_curinga = f"/buscar?nome={urllib.parse.quote('*')}"
    return (
        AnswerSuite(
            ref=f"ldap-injection/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que monta o filtro e faz a busca",
            accepted=("por_nome", "por_nome()"),
            success_feedback="Isso. É em por_nome que o nome entra cru no filtro.",
            failure_feedback="Ainda não. Em services/busca_service.py, veja o único método público da classe.",
        ),
        AnswerSuite(
            ref=f"ldap-injection/answer/comportamento-{r.ramo}-v1",
            version="1.0.0",
            prompt="A busca por * devolve uma pessoa ou o diretório inteiro?",
            accepted=(
                "o diretório inteiro",
                "o diretorio inteiro",
                "diretório inteiro",
                "diretorio inteiro",
                "o diretório todo",
                "o diretorio todo",
                "todo o diretório",
                "todo o diretorio",
                "o diretório",
                "o diretorio",
                "tudo",
                "todos",
                "todas",
            ),
            success_feedback="Exato: o * virou curinga e listou o diretório inteiro de uma vez.",
            failure_feedback="Não é isso. Busque por * e repare que aparecem todas as pessoas, não só uma.",
        ),
        AnswerSuite(
            ref=f"ldap-injection/answer/defesa-{r.ramo}-v1",
            version="1.0.0",
            prompt="O que a busca precisa fazer com os caracteres especiais antes de montar o filtro",
            accepted=(
                "escapar",
                "escapar os caracteres",
                "escapar os caracteres especiais",
                "escape",
                "escapá-los",
                "escapa-los",
                "escapando",
            ),
            success_feedback="Isso. A defesa é escapar os caracteres especiais do filtro.",
            failure_feedback="Ainda não. É o mesmo que se faz para um caractere virar texto, e não sintaxe.",
        ),
        AnswerSuite(
            ref=f"ldap-injection/answer/onde-{r.ramo}-v1",
            version="1.0.0",
            prompt="Depois da correção, o * digitado é tratado como curinga ou como texto?",
            accepted=(
                "texto",
                "como texto",
                "um texto",
                "dado",
                "como dado",
                "um dado",
                "literal",
                "caractere literal",
                "caractere comum",
            ),
            success_feedback="Isso. Escapado, o * deixa de ser curinga e vira texto comum.",
            failure_feedback="Ainda não. O escape tira o poder de sintaxe do caractere; ele passa a ser um valor.",
        ),
        HttpSuite(
            ref=f"ldap-injection/python-flask/busca-protegida-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="a", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="busca-legitima",
                    description="Buscar por um nome real continua achando a pessoa depois da correção.",
                    path=busca_legitima,
                    method="GET",
                    as_user="a",
                    contains=(r.cn_a,),
                ),
                HttpCheck(
                    id="curinga-nao-vaza-tudo",
                    description="Buscar por * não lista mais o diretório inteiro.",
                    path=busca_curinga,
                    method="GET",
                    as_user="a",
                    contains=("Nenhuma pessoa encontrada",),
                    not_contains=(r.cn_outro,),
                ),
            ),
            success_feedback=(
                "Correção validada: buscar por um nome real continua funcionando, e buscar por * não "
                "lista mais o diretório inteiro — a entrada agora é tratada como texto, não como filtro."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste services/busca_service.py "
                "e valide de novo. Escape os caracteres especiais do filtro antes de montar o (cn=...)."
            ),
        ),
    )


# Labs mobile (ADR-025): MOB-01, 02, 04, 05, 08, 09 x 3 ramos (LAB-050 a LAB-067)


@dataclass(frozen=True, slots=True)
class MobRamo:
    ramo: str
    login_a: str  # conta 1 (dona dos itens 1 e 2)
    senha_a: str
    nome_a: str  # trecho ASCII do nome da conta 1
    trecho_proprio: str  # trecho de um item da conta 1
    trecho_outro: str  # trecho de um item da conta 2; só vaza se houver falha
    chave_app: str  # chave embutida no pacote (MOB-01)
    doc_a: str  # documento da conta 1 (MOB-08)
    extra_a: str  # dado pessoal da conta 1 (MOB-08)


MOB_RAMOS = (
    MobRamo(
        "fin",
        "ana.ribeiro",
        "Ana#Pagomais26",
        "Ana Ribeiro",
        "Vale Insumos",
        "Norte Transportes",
        "PGM-APP-KEY-7F3A91C2",
        "111.444.777-35",
        "Renda mensal R$ 9.800",
    ),
    MobRamo(
        "sau",
        "marcos.tavares",
        "Marcos#Lumen26",
        "Marcos Tavares",
        "Hemograma completo",
        "joelho",
        "LUM-APP-KEY-3B71E0C9",
        "333.666.999-57",
        "CID J45 asma",
    ),
    MobRamo(
        "ind",
        "diego.campos",
        "Diego#Aurora26",
        "Diego Campos",
        "bomba 4",
        "turbina 2",
        "AUR-APP-KEY-C40D92B1",
        "MAT-40213",
        "Rua das Turbinas 120",
    ),
)

_SIM = ("sim", "s", "sim, devolveu", "sim devolveu", "yes")
_NAO = ("não", "nao", "n", "não resolve", "nao resolve", "não basta", "nao basta", "no")


def _mob_login(r: MobRamo) -> HttpLogin:
    return HttpLogin(
        name="a",
        path="/api/login",
        json={"login": r.login_a, "senha": r.senha_a},
        token_field="token",  # noqa: S106 - nome do campo JSON, não é senha
    )


def _mob_respostas(
    fam: str,
    r: MobRamo,
    metodo: str,
    comp: tuple[str, ...],
    defesa: tuple[str, ...],
    onde: tuple[str, ...],
    textos: tuple[str, str, str, str],
) -> tuple[Suite, ...]:
    """As quatro etapas de resposta de uma família mobile (método, comportamento, defesa, onde)."""
    ok = ("Isso.", "Exato.", "Isso.", "Isso.")
    return tuple(
        AnswerSuite(
            ref=f"{fam}/answer/{nome}-{r.ramo}-v1",
            version="1.0.0",
            prompt=prompt,
            accepted=aceitos,
            success_feedback=f"{ok[i]} {sucesso}",
            failure_feedback="Ainda não. Releia a etapa e use as dicas, se precisar.",
        )
        for i, (nome, aceitos, (prompt, sucesso)) in enumerate(
            zip(
                ("metodo", "comportamento", "defesa", "onde"),
                ((metodo, f"{metodo}()"), comp, defesa, onde),
                (t.split("|", 1) for t in textos),
                strict=True,
            )
        )
    )


def _mob_chave(r: MobRamo) -> tuple[Suite, ...]:
    fam = "mob-chave-embutida"
    return (
        *_mob_respostas(
            fam,
            r,
            "conta_autorizada",
            _SIM,
            (
                "token",
                "o token",
                "token do usuário",
                "token do usuario",
                "token de sessão",
                "token de sessao",
                "bearer",
                "token bearer",
            ),
            _NAO,
            (
                "Método que decide se o pedido pode ler a lista da conta|É em conta_autorizada que a chave do pacote vale para qualquer conta.",
                "A API devolveu a conta 2 só com a chave, sem login?|Só com a chave do pacote, a API entregou a conta de outra pessoa.",
                "O que o servidor deve exigir no lugar da chave fixa|O token do login identifica o usuário; a chave do app não.",
                "Ofuscar a chave no app resolve?|Quem tem o app consegue montar a chave; a decisão precisa estar no servidor.",
            ),
        ),
        HttpSuite(
            ref=f"{fam}/python-flask/acesso-por-token-{r.ramo}-v1",
            version="1.0.0",
            logins=(_mob_login(r),),
            checks=(
                HttpCheck(
                    id="propria-lista-ok",
                    description="O app, com o token do login, continua lendo a lista da própria conta.",
                    path="/api/itens?conta=1",
                    as_user="a",
                    headers={"X-Api-Key": r.chave_app},
                    contains=(r.trecho_proprio,),
                ),
                HttpCheck(
                    id="so-chave-negada",
                    description="Só com a chave do pacote, sem login, a lista de outra conta é negada.",
                    path="/api/itens?conta=2",
                    headers={"X-Api-Key": r.chave_app},
                    expect_status_in=(401, 403),
                    not_contains=(r.trecho_outro,),
                ),
                HttpCheck(
                    id="outra-conta-negada",
                    description="Com o token de um usuário, a lista de OUTRA conta é negada.",
                    path="/api/itens?conta=2",
                    as_user="a",
                    headers={"X-Api-Key": r.chave_app},
                    expect_status_in=(401, 403),
                    not_contains=(r.trecho_outro,),
                ),
            ),
            success_feedback=(
                "Correção validada: o app continua lendo a própria lista, e a chave do pacote não abre mais "
                "nenhuma conta; só o token do dono libera."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Ajuste services/acesso_service.py: exija o token e confira que "
                "a conta pedida é a dona dele."
            ),
        ),
    )


def _mob_dados_locais(r: MobRamo) -> tuple[Suite, ...]:
    fam = "mob-dados-locais"
    db = "/tmp/dispositivo.db"  # noqa: S108 - caminho do aparelho simulado no contêiner do lab
    return (
        *_mob_respostas(
            fam,
            r,
            "guardar",
            ("senha", "a senha", "senha do usuário", "senha do usuario", "password"),
            ("token", "o token", "token de sessão", "token de sessao", "token do login"),
            _NAO,
            (
                "Método que guarda a sessão no aparelho|É em guardar que o app grava a senha no aparelho.",
                "Qual dado sensível aparece por extenso no aparelho?|A senha ficou escrita por extenso nas preferências do app.",
                "O que basta guardar para manter a sessão|O token mantém a sessão; a senha não precisa ficar no aparelho.",
                "O app precisa guardar a senha no aparelho?|A senha só serve no login; depois, o token basta.",
            ),
        ),
        HttpSuite(
            ref=f"{fam}/python-flask/sem-senha-no-aparelho-{r.ramo}-v1",
            version="1.0.0",
            logins=(_mob_login(r),),
            checks=(
                HttpCheck(
                    id="login-ok",
                    description="Entrar no app continua funcionando.",
                    path="/api/conta",
                    as_user="a",
                    contains=(r.nome_a,),
                ),
            ),
            inspections=(
                InspectCheck(
                    id="token-guardado-sem-senha",
                    description="O aparelho guarda a sessão (há preferências gravadas) e nenhum valor é a senha.",
                    db_path=db,
                    query="SELECT chave, valor FROM prefs",
                    min_rows=1,
                    none_match=re.escape(r.senha_a),
                ),
                InspectCheck(
                    id="sem-chave-de-senha",
                    description="Nenhuma preferência guarda a senha de outra forma (nem hash, nem cifrada).",
                    db_path=db,
                    query="SELECT chave, valor FROM prefs WHERE lower(chave) LIKE '%senha%' OR lower(chave) LIKE '%pass%'",
                    min_rows=0,
                    none_match=r"[\s\S]",
                ),
            ),
            success_feedback=(
                "Correção validada: o login continua funcionando e o aparelho guarda só o token, sem a senha."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Ajuste dispositivo/sessao_local.py: grave só o login e o token."
            ),
        ),
    )


def _mob_biometria(r: MobRamo) -> tuple[Suite, ...]:
    fam = "mob-biometria-cliente"
    return (
        *_mob_respostas(
            fam,
            r,
            "executar",
            _SIM,
            (
                "prova",
                "a prova",
                "prova da biometria",
                "prova de biometria",
                "a prova da biometria",
                "prova da digital",
                "assinatura",
            ),
            ("servidor", "o servidor", "backend", "o backend", "a api", "api"),
            (
                "Método que executa a operação|É em executar que falta conferir a prova da digital.",
                "A operação foi executada sem a digital?|Sem conferir no servidor, a digital vira enfeite.",
                "O que o servidor precisa conferir antes de executar|O servidor confere a prova da biometria.",
                "Quem deve decidir se a digital foi exigida?|O app está nas mãos do atacante; quem decide é o servidor.",
            ),
        ),
        HttpSuite(
            ref=f"{fam}/python-flask/prova-exigida-{r.ramo}-v1",
            version="1.0.0",
            logins=(_mob_login(r),),
            checks=(
                HttpCheck(
                    id="pede-prova",
                    description="Depois da digital, o app recebe a prova da biometria.",
                    path="/api/biometria/prova",
                    method="POST",
                    as_user="a",
                    capture={"prova": r'"prova"\s*:\s*"([0-9a-f]+)"'},
                ),
                HttpCheck(
                    id="com-prova-ok",
                    description="Com a prova válida da biometria, a operação continua funcionando.",
                    path="/api/acao",
                    method="POST",
                    as_user="a",
                    headers={"X-Prova-Biometria": "{{prova}}"},
                    contains=("executada",),
                ),
                HttpCheck(
                    id="sem-prova-negada",
                    description="Sem a prova da biometria, o servidor recusa a operação.",
                    path="/api/acao",
                    method="POST",
                    as_user="a",
                    expect_status_in=(401, 403),
                    not_contains=("executada",),
                ),
                HttpCheck(
                    id="prova-falsa-negada",
                    description="Com uma prova inventada, o servidor recusa a operação.",
                    path="/api/acao",
                    method="POST",
                    as_user="a",
                    headers={"X-Prova-Biometria": "00000000000000000000000000000000"},
                    expect_status_in=(401, 403),
                    not_contains=("executada",),
                ),
            ),
            success_feedback=(
                "Correção validada: com a prova da digital a operação funciona; sem prova ou com prova inventada, "
                "o servidor recusa."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Ajuste services/acao_service.py: confira a prova com "
                "self._provas.valida antes de executar."
            ),
        ),
    )


def _mob_logout(r: MobRamo) -> tuple[Suite, ...]:
    fam = "mob-sessao-logout"
    return (
        *_mob_respostas(
            fam,
            r,
            "sair",
            _SIM,
            (
                "revogar",
                "revogá-lo",
                "revoga-lo",
                "revoga",
                "invalidar",
                "invalida",
                "inativar",
                "desativar",
                "cancelar",
                "expirar",
                "apagar",
            ),
            _NAO,
            (
                "Método que encerra a sessão|É em sair que o servidor deveria encerrar a sessão.",
                "Depois do logout, o token antigo abriu a conta?|O token continuou valendo depois do logout.",
                "O que o servidor faz com o token no logout|No logout, o servidor revoga o token.",
                "Apagar o token só no aparelho encerra a sessão?|Cópias do token continuam valendo até o servidor revogar.",
            ),
        ),
        HttpSuite(
            ref=f"{fam}/python-flask/logout-revoga-{r.ramo}-v1",
            version="1.0.0",
            logins=(_mob_login(r),),
            checks=(
                HttpCheck(
                    id="antes-ok",
                    description="Com a sessão aberta, o app lê a conta normalmente.",
                    path="/api/conta",
                    as_user="a",
                    contains=(r.nome_a,),
                ),
                HttpCheck(
                    id="logout",
                    description="O app pede o logout.",
                    path="/api/sair",
                    method="POST",
                    as_user="a",
                    expect_status_in=(200, 204),
                ),
                HttpCheck(
                    id="token-antigo-negado",
                    description="Depois do logout, o mesmo token é recusado.",
                    path="/api/conta",
                    as_user="a",
                    expect_status_in=(401, 403),
                    not_contains=(r.nome_a,),
                ),
            ),
            success_feedback="Correção validada: depois do logout, o token antigo não abre mais a conta.",
            failure_feedback=(
                "Algumas verificações falharam. Ajuste services/sessao_service.py: revogue o token no logout."
            ),
        ),
    )


def _mob_dados_demais(r: MobRamo) -> tuple[Suite, ...]:
    fam = "mob-dados-demais"
    return (
        *_mob_respostas(
            fam,
            r,
            "perfil",
            _SIM,
            (
                "minimização",
                "minimizacao",
                "minimização de dados",
                "minimizacao de dados",
                "minimizar",
                "princípio da minimização",
                "principio da minimizacao",
                "necessidade",
            ),
            _NAO,
            (
                "Método que monta os dados do perfil|É em perfil que a API devolve o registro inteiro.",
                "A resposta traz dados que a tela não mostra?|A API entrega ao aparelho bem mais do que a tela mostra.",
                "Nome do princípio de privacidade|Minimização: só sai do servidor o que a tela precisa.",
                "Esconder os campos na tela resolve?|O dado já saiu do servidor; a tela não é o filtro.",
            ),
        ),
        HttpSuite(
            ref=f"{fam}/python-flask/perfil-minimo-{r.ramo}-v1",
            version="1.0.0",
            logins=(_mob_login(r),),
            checks=(
                HttpCheck(
                    id="tela-ok",
                    description="A tela Perfil continua recebendo o nome e o resumo.",
                    path="/api/perfil",
                    as_user="a",
                    contains=(r.nome_a, '"resumo"'),
                ),
                HttpCheck(
                    id="sem-dados-pessoais",
                    description="A resposta não traz o documento nem o dado pessoal da conta.",
                    path="/api/perfil",
                    as_user="a",
                    not_contains=(r.doc_a, r.extra_a),
                ),
            ),
            success_feedback="Correção validada: a API entrega só nome e resumo, sem dados pessoais.",
            failure_feedback=(
                "Algumas verificações falharam. Ajuste services/perfil_service.py: devolva só nome e resumo."
            ),
        ),
    )


def _mob_modo_teste(r: MobRamo) -> tuple[Suite, ...]:
    fam = "mob-modo-teste"
    return (
        *_mob_respostas(
            fam,
            r,
            "identificar",
            _SIM,
            ("x-debug", "x-debug: 1", "x-debug:1", "cabeçalho x-debug", "cabecalho x-debug"),
            _NAO,
            (
                "Método que identifica o usuário do pedido|É em identificar que ficou o atalho de homologação.",
                "Sem login e com X-Debug: 1, a API devolveu uma conta?|O atalho de teste abriu uma conta sem login.",
                "Cabeçalho que liga o atalho|X-Debug é escrito por quem envia o pedido, inclusive o atacante.",
                "O atalho deveria existir em produção?|Atalho de teste fica fora do build de produção.",
            ),
        ),
        HttpSuite(
            ref=f"{fam}/python-flask/sem-atalho-{r.ramo}-v1",
            version="1.0.0",
            logins=(_mob_login(r),),
            checks=(
                HttpCheck(
                    id="login-ok",
                    description="Com o token do login, o app lê a conta normalmente.",
                    path="/api/conta",
                    as_user="a",
                    contains=(r.nome_a,),
                ),
                HttpCheck(
                    id="atalho-negado",
                    description="Sem login, com X-Debug: 1, a API recusa o pedido.",
                    path="/api/conta",
                    headers={"X-Debug": "1"},
                    expect_status_in=(401, 403),
                    not_contains=(r.nome_a,),
                ),
            ),
            success_feedback="Correção validada: o login continua funcionando e o X-Debug não abre mais conta nenhuma.",
            failure_feedback=(
                "Algumas verificações falharam. Ajuste services/identidade_service.py: remova o atalho do X-Debug."
            ),
        ),
    )


# --------------------------------------------------------------------------------------------------
# Lacunas dos Cursos OWASP. L5 api-inventario: versão 1 da API esquecida no ar (LAB-068 a LAB-070)


def _sem_acento(texto: str) -> str:
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def _com_variantes(*valores: str) -> tuple[str, ...]:
    """Cada valor com e sem acento (a comparação ignora maiúsculas e espaços extras, mas não acentos)."""
    saida: list[str] = []
    for v in valores:
        for w in (v, _sem_acento(v)):
            if w not in saida:
                saida.append(w)
    return tuple(saida)


@dataclass(frozen=True, slots=True)
class InventarioRamo:
    ramo: str
    recurso: str  # segmento da rota: /api/v2/<recurso>/<id>
    login_a: str
    senha_a: str
    doc_a: int
    titulo_a: str  # trecho do título do documento da conta A
    doc_b: int
    nome_b: str  # titular do documento de outra conta
    detalhe_b: str  # trecho do detalhe do documento de outra conta


INVENTARIO_RAMOS = (
    InventarioRamo(
        "fin",
        "comprovantes",
        "larissa.prado",
        "Larissa#Cobalto26",
        101,
        "Mercado Bom",
        201,
        "Rogério Tavares Lima",
        "Lar Certo",
    ),
    InventarioRamo(
        "sau",
        "exames",
        "beatriz.moura",
        "Beatriz#Iris26",
        101,
        "Hemograma",
        201,
        "Otávio Ramos Bezerra",
        "hepatite",
    ),
    InventarioRamo(
        "ind",
        "faturas",
        "compras.metalfort",
        "Metalfort#Serra26",
        101,
        "unidade Contagem",
        201,
        "Têxtil Vale Verde S.A.",
        "Americana",
    ),
)


def _inventario(r: InventarioRamo) -> tuple[Suite, ...]:
    primeiro, *_, ultimo = r.nome_b.replace(" S.A.", "").split()
    return (
        AnswerSuite(
            ref=f"api-inventario/answer/versao-{r.ramo}-v1",
            version="1.0.0",
            prompt="Versão da API que a documentação publica",
            accepted=("v2", "2", "versão 2", "versao 2", "/api/v2", "api/v2"),
            success_feedback="Isso. A documentação só fala da v2.",
            failure_feedback="Ainda não. Veja o texto 'Versão publicada' no topo da documentação.",
        ),
        AnswerSuite(
            ref=f"api-inventario/answer/arquivo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Arquivo do controller da versão que não está na documentação",
            accepted=(
                "api_v1_controller.py",
                "api_v1_controller",
                "controllers/api_v1_controller.py",
                "workspace/controllers/api_v1_controller.py",
            ),
            success_feedback="Isso. A v1 continua registrada em app.py, mesmo fora da documentação.",
            failure_feedback="Ainda não. Em app.py, veja de qual arquivo vem o blueprint api_v1_bp.",
        ),
        AnswerSuite(
            ref=f"api-inventario/answer/titular-{r.ramo}-v1",
            version="1.0.0",
            prompt="Titular que aparece na resposta da v1",
            accepted=_com_variantes(r.nome_b, r.nome_b.replace(" S.A.", ""), f"{primeiro} {ultimo}"),
            success_feedback="Exato: pela v1 você leu o documento de outro cliente, que a v2 recusava.",
            failure_feedback="Ainda não. Abra a rota da v1 com o número da tarefa e copie o campo titular.",
        ),
        AnswerSuite(
            ref=f"api-inventario/answer/conceito-{r.ramo}-v1",
            version="1.0.0",
            prompt="Nome da lista viva de APIs, versões e rotas publicadas",
            accepted=_com_variantes(
                "inventário", "inventário de api", "inventário de apis", "gestão de inventário", "inventory"
            ),
            success_feedback="Isso. Sem inventário, a v1 ficou no ar sem dono e sem data para desligar.",
            failure_feedback="Ainda não. É a palavra do item API9 da OWASP 2023.",
        ),
        HttpSuite(
            ref=f"api-inventario/python-flask/versao-antiga-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="cliente", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="v2-continua",
                    description="A v2 continua entregando o documento da própria conta.",
                    path=f"/api/v2/{r.recurso}/{r.doc_a}",
                    as_user="cliente",
                    contains=(r.titulo_a,),
                ),
                HttpCheck(
                    id="v2-protege",
                    description="A v2 continua recusando o documento de outra conta.",
                    path=f"/api/v2/{r.recurso}/{r.doc_b}",
                    as_user="cliente",
                    expect_status=404,
                    not_contains=(r.detalhe_b,),
                ),
                HttpCheck(
                    id="v1-nao-vaza",
                    description="A v1 não devolve mais o documento de outra conta (410, 404 ou 403).",
                    path=f"/api/v1/{r.recurso}/{r.doc_b}",
                    as_user="cliente",
                    expect_status_in=(403, 404, 410),
                    not_contains=(r.detalhe_b, r.nome_b),
                ),
            ),
            success_feedback=(
                "Correção validada: a v1 não entrega mais documentos de outros clientes, e a v2 continua "
                "funcionando para o dono."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo, ajuste "
                "controllers/api_v1_controller.py e valide de novo. Esconder a rota da documentação não basta."
            ),
        ),
    )


# L6 api-consumo-parceiro: resposta do parceiro gravada sem conferir o contrato (LAB-071 a LAB-073)


@dataclass(frozen=True, slots=True)
class ConsumoRamo:
    ramo: str
    banco: str  # arquivo SQLite do lab (/tmp/<banco>.db)
    login_a: str
    senha_a: str
    ref_a: str
    teto: int


CONSUMO_RAMOS = (
    ConsumoRamo("fin", "vertix_credito", "renata.quintela", "Renata#Vertix26", "PROP-4471", 50000),
    ConsumoRamo("sau", "bemcuidar_reembolso", "helena.barros", "Helena#BemCuidar26", "REEMB-2093", 20000),
    ConsumoRamo("ind", "alvorada_compras", "marcos.teixeira", "Marcos#Alvorada26", "COT-7781", 10000),
)


def _consumo(r: ConsumoRamo) -> tuple[Suite, ...]:
    banco = f"/tmp/{r.banco}.db"  # noqa: S108 - caminho do banco DENTRO do contêiner do lab
    return (
        AnswerSuite(
            ref=f"api-consumo-parceiro/answer/cliente-{r.ramo}-v1",
            version="1.0.0",
            prompt="Arquivo que faz a chamada HTTP ao parceiro",
            accepted=("parceiro_client.py", "parceiro_client", "services/parceiro_client.py"),
            success_feedback="Isso. O cliente só busca a resposta; quem decide o que gravar é outro arquivo.",
            failure_feedback="Ainda não. Procure em services/ o arquivo com urllib.request.urlopen.",
        ),
        AnswerSuite(
            ref=f"api-consumo-parceiro/answer/status-{r.ramo}-v1",
            version="1.0.0",
            prompt="Status que a consulta recebeu com o parceiro comprometido",
            accepted=("aprovado", "aprovada", "aprovou"),
            success_feedback="Exato: um campo fora do contrato aprovou a consulta sozinho.",
            failure_feedback="Ainda não. Veja a coluna Status da linha mais nova em Consultas gravadas.",
        ),
        AnswerSuite(
            ref=f"api-consumo-parceiro/answer/contrato-{r.ramo}-v1",
            version="1.0.0",
            prompt="Nome do acordo sobre campos, tipos e faixas da resposta",
            accepted=_com_variantes(
                "contrato", "contrato da api", "contrato de api", "esquema", "schema", "contract"
            ),
            success_feedback="Isso. O contrato é a régua para recusar o que vier fora.",
            failure_feedback="Ainda não. Veja o comentário do topo de services/consulta_service.py.",
        ),
        AnswerSuite(
            ref=f"api-consumo-parceiro/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que grava a resposta do parceiro sem conferir",
            accepted=("registrar", "registrar()", "ConsultaService.registrar"),
            success_feedback="Isso. É em registrar que a resposta precisa ser conferida.",
            failure_feedback="Ainda não. Veja o único método público de ConsultaService.",
        ),
        HttpSuite(
            ref=f"api-consumo-parceiro/python-flask/contrato-parceiro-{r.ramo}-v1",
            version="1.0.0",
            logins=(
                HttpLogin(name="analista", path="/login", form={"login": r.login_a, "senha": r.senha_a}),
            ),
            checks=(
                HttpCheck(
                    id="parceiro-normal",
                    description="Com o parceiro normal, a consulta continua sendo gravada.",
                    path="/parceiro/admin/modo",
                    method="POST",
                    form={"modo": "normal"},
                    expect_status_in=(200, 302),
                ),
                HttpCheck(
                    id="consulta-normal-gravada",
                    description="A resposta dentro do contrato é aceita e gravada em análise.",
                    path="/consultas",
                    method="POST",
                    form={"referencia": r.ref_a},
                    as_user="analista",
                    contains=("gravada", "em análise"),
                ),
                HttpCheck(
                    id="parceiro-comprometido",
                    description="A suíte simula o parceiro comprometido.",
                    path="/parceiro/admin/modo",
                    method="POST",
                    form={"modo": "comprometido"},
                    expect_status_in=(200, 302),
                ),
                HttpCheck(
                    id="resposta-adulterada-recusada",
                    description="A resposta fora do contrato é recusada e nada é gravado.",
                    path="/consultas",
                    method="POST",
                    form={"referencia": r.ref_a},
                    as_user="analista",
                    expect_status_in=(400, 422, 502),
                ),
            ),
            inspections=(
                InspectCheck(
                    id="valores-na-faixa",
                    description=f"Nenhum valor gravado fica fora da faixa de 0 a {r.teto}.",
                    db_path=banco,
                    # teto é constante da suíte, não entrada do aluno
                    query=f"SELECT referencia, IIF(valor BETWEEN 0 AND {r.teto}, 'ok', 'fora') FROM consultas",  # noqa: S608
                    all_match=r"^ok$",
                ),
                InspectCheck(
                    id="status-decidido-pelo-app",
                    description="Nenhuma consulta é aprovada por um campo vindo do parceiro.",
                    db_path=banco,
                    query="SELECT referencia, status FROM consultas",
                    none_match=r"aprovad",
                ),
            ),
            success_feedback=(
                "Correção validada: a resposta dentro do contrato continua sendo gravada, e a resposta "
                "adulterada do parceiro é recusada sem tocar no banco."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo e ajuste "
                "services/consulta_service.py: confira os campos e a faixa e grave sempre 'em análise'."
            ),
        ),
    )


# L7 api-recursos: listagem sem teto de página (LAB-074 a LAB-076)


@dataclass(frozen=True, slots=True)
class RecursosRamo:
    ramo: str
    recurso: str  # rota /api/<recurso>
    prefixo: str  # prefixo da descrição de cada item (LCT-00001, ...)
    login_a: str
    senha_a: str
    total: int


RECURSOS_RAMOS = (
    RecursosRamo("fin", "lancamentos", "LCT-", "eduardo.saraiva", "Eduardo#Pinaculo26", 3000),
    RecursosRamo("sau", "atendimentos", "ATD-", "patricia.lins", "Patricia#Sereno26", 3000),
    RecursosRamo("ind", "leituras", "LEI-", "tiago.andrade", "Tiago#Ventura26", 3000),
)


def _recursos(r: RecursosRamo) -> tuple[Suite, ...]:
    alem_do_teto = f"{r.prefixo}00101"
    return (
        AnswerSuite(
            ref=f"api-recursos/answer/quantidade-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor de quantidade com limite=20",
            accepted=("20", "vinte"),
            success_feedback="Isso. O app pede 20 itens por vez.",
            failure_feedback="Ainda não. Abra o link do painel e veja o campo quantidade.",
        ),
        AnswerSuite(
            ref=f"api-recursos/answer/total-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor de quantidade com limite=100000",
            accepted=(str(r.total), f"{r.total:,}".replace(",", "."), f"{r.total:,}"),
            success_feedback="Exato: uma chamada trouxe a base inteira da conta.",
            failure_feedback="Ainda não. Use a rota da tarefa e copie o campo quantidade.",
        ),
        AnswerSuite(
            ref=f"api-recursos/answer/negativo-{r.ramo}-v1",
            version="1.0.0",
            prompt="O limite -1 devolveu tudo ou nada?",
            accepted=("tudo", "todos", "tudo veio", "todos os itens", "all"),
            success_feedback="Isso. No SQLite, LIMIT -1 é 'sem limite': o negativo também abre tudo.",
            failure_feedback="Não é isso. Compare a quantidade com a da etapa anterior.",
        ),
        AnswerSuite(
            ref=f"api-recursos/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método do serviço que usa o limite sem teto",
            accepted=("listar", "listar()"),
            success_feedback="Isso. É em listar que o teto precisa ser aplicado.",
            failure_feedback="Ainda não. Veja o único método público da classe do serviço.",
        ),
        HttpSuite(
            ref=f"api-recursos/python-flask/teto-pagina-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="cliente", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="pagina-normal",
                    description="O app continua recebendo a página de 20 itens.",
                    path=f"/api/{r.recurso}?limite=20&pagina=1",
                    as_user="cliente",
                    contains=(f"{r.prefixo}00020",),
                    not_contains=(f"{r.prefixo}00021",),
                ),
                HttpCheck(
                    id="limite-grande-contido",
                    description="Um limite enorme não traz mais que 100 itens.",
                    path=f"/api/{r.recurso}?limite=100000",
                    as_user="cliente",
                    expect_status_in=(200, 400),
                    not_contains=(alem_do_teto,),
                ),
                HttpCheck(
                    id="limite-negativo-contido",
                    description="Um limite negativo não abre a base inteira.",
                    path=f"/api/{r.recurso}?limite=-1",
                    as_user="cliente",
                    expect_status_in=(200, 400),
                    not_contains=(alem_do_teto,),
                ),
            ),
            success_feedback=(
                "Correção validada: o app continua com a página de 20, e nem um limite enorme nem um "
                "negativo trazem mais que o teto."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo e ajuste o método listar do "
                "serviço: prenda o limite entre 1 e LIMITE_MAXIMO."
            ),
        ),
    )


# L2 log-auditoria: login sem registro das falhas (LAB-077 a LAB-079)


@dataclass(frozen=True, slots=True)
class AuditoriaRamo:
    ramo: str
    banco: str  # arquivo SQLite do lab (/tmp/<banco>.db)
    login_a: str
    senha_a: str


AUDITORIA_RAMOS = (
    AuditoriaRamo("fin", "portal_corretor", "patricia.moura", "Patricia#MareAlta26"),
    AuditoriaRamo("sau", "sanare_prestador", "dra.helena.castro", "Helena#Sanare26"),
    AuditoriaRamo("ind", "luz_do_vale_operacao", "marcos.teixeira", "Marcos#LuzDoVale26"),
)

# Senha errada FICTÍCIA que a suíte digita; ela não pode aparecer na trilha.
_SENHA_ERRADA_SUITE = "Tentativa#Errada77"
_LOGIN_INEXISTENTE_SUITE = "conta.que.nao.existe"


def _auditoria(r: AuditoriaRamo) -> tuple[Suite, ...]:
    banco = f"/tmp/{r.banco}.db"  # noqa: S108 - caminho do banco DENTRO do contêiner do lab
    trilha = "SELECT id, evento || '|' || login || '|' || ip FROM auditoria"
    return (
        AnswerSuite(
            ref=f"log-auditoria/answer/evento-{r.ramo}-v1",
            version="1.0.0",
            prompt="Evento que aparece na tabela do painel",
            accepted=("login_ok", "login ok", "loginok"),
            success_feedback="Isso. O login certo deixa o evento login_ok na trilha.",
            failure_feedback="Ainda não. Copie o texto da coluna Evento da tabela do painel.",
        ),
        AnswerSuite(
            ref=f"log-auditoria/answer/falhas-{r.ramo}-v1",
            version="1.0.0",
            prompt="Quantas tentativas com senha errada aparecem na tabela",
            accepted=("0", "zero", "nenhuma", "nenhum"),
            success_feedback="Exato: as tentativas erradas não deixaram rastro nenhum.",
            failure_feedback="Ainda não. Conte as linhas da tabela que não são login_ok.",
        ),
        AnswerSuite(
            ref=f"log-auditoria/answer/segredo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Dado do formulário que nunca pode ir para a auditoria",
            accepted=_com_variantes("senha", "a senha", "password", "senha digitada"),
            success_feedback="Isso. Senha, certa ou errada, nunca vai para log nem auditoria.",
            failure_feedback="Não é isso. O login pode ser registrado; pense no outro campo do formulário.",
        ),
        AnswerSuite(
            ref=f"log-auditoria/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que confere a senha e decide o que vai para a auditoria",
            accepted=("autenticar", "autenticar()", "AuthService.autenticar"),
            success_feedback="Isso. É em autenticar que a falha precisa ser registrada.",
            failure_feedback="Ainda não. Veja o único método público de AuthService.",
        ),
        HttpSuite(
            ref=f"log-auditoria/python-flask/auditoria-login-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="usuario", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="login-certo-continua",
                    description="Quem entra com a senha certa continua chegando ao painel.",
                    path="/painel",
                    as_user="usuario",
                    contains=("Atividade de segurança",),
                ),
                HttpCheck(
                    id="senha-errada-recusada",
                    description="A senha errada continua sendo recusada.",
                    path="/login",
                    method="POST",
                    form={"login": r.login_a, "senha": _SENHA_ERRADA_SUITE},
                    contains=("inválidos",),
                ),
                HttpCheck(
                    id="login-inexistente-recusado",
                    description="Um login que não existe continua sendo recusado.",
                    path="/login",
                    method="POST",
                    form={"login": _LOGIN_INEXISTENTE_SUITE, "senha": _SENHA_ERRADA_SUITE},
                    contains=("inválidos",),
                ),
            ),
            inspections=(
                InspectCheck(
                    id="falha-registrada",
                    description="A senha errada deixa um evento login_falhou com o login tentado.",
                    db_path=banco,
                    query=f"SELECT id, evento FROM auditoria WHERE login = '{r.login_a}' AND evento = 'login_falhou'",  # noqa: S608
                ),
                InspectCheck(
                    id="login-inexistente-registrado",
                    description="A tentativa com um login que não existe também é registrada.",
                    db_path=banco,
                    query="SELECT id, evento FROM auditoria WHERE login = 'conta.que.nao.existe' AND evento = 'login_falhou'",
                ),
                InspectCheck(
                    id="sucesso-registrado",
                    description="O login certo continua registrado como login_ok.",
                    db_path=banco,
                    query=f"SELECT id, evento FROM auditoria WHERE login = '{r.login_a}' AND evento = 'login_ok'",  # noqa: S608
                ),
                InspectCheck(
                    id="sem-senha-na-trilha",
                    description="Nenhuma senha, certa ou errada, aparece na trilha de auditoria.",
                    db_path=banco,
                    query=trilha,
                    min_rows=1,
                    none_match=f"{re.escape(_SENHA_ERRADA_SUITE)}|{re.escape(r.senha_a)}",
                ),
            ),
            success_feedback=(
                "Correção validada: o login certo e as tentativas erradas, inclusive de um login que não "
                "existe, ficam na trilha com login e IP, e nenhuma senha é gravada."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo e ajuste o método autenticar de "
                "services/auth_service.py: registre login_falhou em todo caminho de falha, sem a senha."
            ),
        ),
    )


# L1 componente-desatualizado: dependência com falha conhecida (LAB-080 a LAB-082)


@dataclass(frozen=True, slots=True)
class ComponenteRamo:
    ramo: str
    login_a: str
    senha_a: str
    nome_a: str


COMPONENTE_RAMOS = (
    ComponenteRamo("fin", "camila.rezende", "Camila#Altiva26", "Camila Rezende Prado"),
    ComponenteRamo("sau", "renata.vilela", "Renata#Prisma26", "Renata Vilela Moura"),
    ComponenteRamo("ind", "diego.carvalho", "Diego#FerroNorte26", "Diego Carvalho Neves"),
)

# Marcador da primeira linha de config/integracoes_demo.ini, o arquivo interno FICTÍCIO do lab.
_MARCADOR_INTERNO = "INTEGRACOES-DEMO"


def _componente(r: ComponenteRamo) -> tuple[Suite, ...]:
    return (
        AnswerSuite(
            ref=f"componente-desatualizado/answer/versao-{r.ramo}-v1",
            version="1.0.0",
            prompt="Versão da relatorix que a aplicação usa",
            accepted=("2.1.0", "2.1", "relatorix==2.1.0", "v2.1.0"),
            success_feedback="Isso. É a versão fixada desde que o sistema entrou no ar.",
            failure_feedback="Ainda não. Veja a linha da relatorix em requirements.txt, depois do ==.",
        ),
        AnswerSuite(
            ref=f"componente-desatualizado/answer/corrigida-{r.ramo}-v1",
            version="1.0.0",
            prompt="Versão da relatorix que corrige a falha",
            accepted=("2.4.1", "relatorix==2.4.1", "v2.4.1"),
            success_feedback="Isso. A 2.1.0 está na faixa afetada, e a 2.4.1 é a corrigida.",
            failure_feedback="Ainda não. Veja a tabela de versões do aviso em avisos/.",
        ),
        AnswerSuite(
            ref=f"componente-desatualizado/answer/marcador-{r.ramo}-v1",
            version="1.0.0",
            prompt="Texto da primeira linha do arquivo interno",
            accepted=_com_variantes(_MARCADOR_INTERNO.lower(), "; integracoes-demo", "integracoes demo"),
            success_feedback="Exato: o gerador de documentos entregou um arquivo de configuração interno.",
            failure_feedback="Ainda não. Rode os dois comandos curl da tarefa e copie o texto depois do ;.",
        ),
        AnswerSuite(
            ref=f"componente-desatualizado/answer/arquivo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Arquivo onde a versão da relatorix é fixada",
            accepted=("requirements.txt", "requirements", "/workspace/requirements.txt"),
            success_feedback="Isso. É lá que se troca a versão fixada.",
            failure_feedback="Ainda não. É o arquivo de dependências que você abriu na etapa 1.",
        ),
        HttpSuite(
            ref=f"componente-desatualizado/python-flask/versao-corrigida-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="usuario", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="documento-padrao",
                    description="O documento no modelo padrão continua sendo gerado.",
                    path="/documento?modelo=padrao.html",
                    as_user="usuario",
                    contains=(r.nome_a,),
                ),
                HttpCheck(
                    id="documento-detalhado",
                    description="O modelo detalhado também continua funcionando.",
                    path="/documento?modelo=detalhado.html",
                    as_user="usuario",
                    contains=(r.nome_a, "detalhado"),
                ),
                HttpCheck(
                    id="modelo-fora-da-pasta",
                    description="Um modelo com ../ não abre arquivos de fora da pasta de modelos.",
                    path="/documento?modelo=../config/integracoes_demo.ini",
                    as_user="usuario",
                    expect_status_in=(200, 400, 403, 404),
                    not_contains=(_MARCADOR_INTERNO,),
                ),
                HttpCheck(
                    id="modelo-codificado",
                    description="A forma codificada do ../ também não sai da pasta de modelos.",
                    path="/documento?modelo=%252e%252e%252fconfig%252fintegracoes_demo.ini",
                    as_user="usuario",
                    expect_status_in=(200, 400, 403, 404),
                    not_contains=(_MARCADOR_INTERNO,),
                ),
                HttpCheck(
                    id="caminho-absoluto",
                    description="Um caminho absoluto também não sai da pasta de modelos.",
                    path="/documento?modelo=/workspace/config/integracoes_demo.ini",
                    as_user="usuario",
                    expect_status_in=(200, 400, 403, 404),
                    not_contains=(_MARCADOR_INTERNO,),
                ),
            ),
            success_feedback=(
                "Correção validada: com a relatorix 2.4.1, os modelos legítimos continuam funcionando e "
                "nenhuma forma de nome sai da pasta de modelos."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo. A correção é atualizar a "
                "relatorix em requirements.txt para a versão corrigida do aviso; um filtro de texto no "
                "código não cobre a forma codificada."
            ),
        ),
    )


# L4 pacote-assinatura: pacote aplicado sem conferir a assinatura HMAC (LAB-083 a LAB-085)


@dataclass(frozen=True, slots=True)
class PacoteRamo:
    ramo: str
    banco: str  # arquivo SQLite do lab (/tmp/<banco>.db)
    login_a: str
    senha_a: str
    fornecedor: str
    versao: str
    parametros: tuple[tuple[str, int | float], ...]
    chave: str  # chave HMAC FICTÍCIA do lab (config.py)
    param: str  # parâmetro que a suíte adultera
    valor_mal: int | float


PACOTE_RAMOS = (
    PacoteRamo(
        "fin",
        "solaris_antifraude",
        "beatriz.nogueira",
        "Beatriz#Solaris26",
        "Bureau Atento Antifraude",
        "2026.11.1",
        (("limite_pix_noturno", 1000), ("score_minimo_aprovacao", 720), ("dias_dispositivo_novo", 3)),
        "lab-fin-chave-hmac-ficticia-bureau-2026",
        "limite_pix_noturno",
        50000,
    ),
    PacoteRamo(
        "sau",
        "bompastor_alertas",
        "luciana.ferraz",
        "Luciana#BomPastor26",
        "Laboratório de Apoio Analítica",
        "2026.11.1",
        (("glicemia_critica_min", 50), ("hemoglobina_critica_min", 7.0), ("potassio_critico_max", 6.0)),
        "lab-sau-chave-hmac-ficticia-analitica-2026",
        "potassio_critico_max",
        9.0,
    ),
    PacoteRamo(
        "ind",
        "cruzeiro_parametros",
        "rafael.antunes",
        "Rafael#Cruzeiro26",
        "Integradora Vértice Automação",
        "2026.11.1",
        (
            ("pressao_max_hidraulica", 210),
            ("temperatura_max_forno", 1250),
            ("velocidade_max_laminador", 11.5),
        ),
        "lab-ind-chave-hmac-ficticia-vertice-2026",
        "temperatura_max_forno",
        1600,
    ),
)


def _pacote_assinado(r: PacoteRamo) -> dict[str, object]:
    """O pacote legítimo do fornecedor, assinado como o lab espera (HMAC-SHA256 do conteúdo canônico)."""
    pacote: dict[str, object] = {
        "fornecedor": r.fornecedor,
        "versao": r.versao,
        "parametros": dict(r.parametros),
    }
    canonico = json.dumps(pacote, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    pacote["assinatura"] = hmac.new(r.chave.encode("utf-8"), canonico, hashlib.sha256).hexdigest()
    return pacote


def _pacote(r: PacoteRamo) -> tuple[Suite, ...]:
    banco = f"/tmp/{r.banco}.db"  # noqa: S108 - caminho do banco DENTRO do contêiner do lab
    legitimo = _pacote_assinado(r)
    adulterado = {**legitimo, "parametros": {**dict(r.parametros), r.param: r.valor_mal}}
    sem_assinatura = {k: v for k, v in adulterado.items() if k != "assinatura"}
    valor_ok = str(dict(r.parametros)[r.param])

    def envio(nome: str, pacote: dict[str, object]) -> dict[str, str]:
        # ensure_ascii: o probe envia o arquivo em latin-1; com os acentos escapados no JSON, chega igual.
        conteudo = json.dumps(pacote, indent=2, ensure_ascii=True)
        return {"field": "arquivo", "filename": nome, "content_type": "application/json", "content": conteudo}

    return (
        AnswerSuite(
            ref=f"pacote-assinatura/answer/campo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Campo do pacote que leva a assinatura do fornecedor",
            accepted=("assinatura", '"assinatura"', "assinatura hmac"),
            success_feedback="Isso. É o HMAC que o fornecedor calculou sobre o conteúdo.",
            failure_feedback="Ainda não. Procure o campo com um texto longo em hexadecimal.",
        ),
        AnswerSuite(
            ref=f"pacote-assinatura/answer/valor-{r.ramo}-v1",
            version="1.0.0",
            prompt="Valor do parâmetro em vigor depois do envio alterado",
            accepted=_com_variantes(str(r.valor_mal), str(r.valor_mal).replace(".", ",")),
            success_feedback="Exato: o pacote alterado virou regra, com a assinatura antiga no lugar.",
            failure_feedback="Ainda não. Recarregue a aba Aplicação e veja a linha do parâmetro alterado.",
        ),
        AnswerSuite(
            ref=f"pacote-assinatura/answer/garantia-{r.ramo}-v1",
            version="1.0.0",
            prompt="O que a assinatura garante além da integridade",
            accepted=_com_variantes("origem", "autenticidade", "procedência", "autoria", "a origem"),
            success_feedback="Isso. Integridade e origem: não mudou e veio de quem tem a chave.",
            failure_feedback="Não é isso. Pense em de quem o pacote veio.",
        ),
        AnswerSuite(
            ref=f"pacote-assinatura/answer/metodo-{r.ramo}-v1",
            version="1.0.0",
            prompt="Método que aplica o pacote sem conferir a assinatura",
            accepted=("importar", "importar()", "PacoteService.importar"),
            success_feedback="Isso. É em importar que a assinatura precisa ser conferida.",
            failure_feedback="Ainda não. Veja o único método público de PacoteService.",
        ),
        HttpSuite(
            ref=f"pacote-assinatura/python-flask/assinatura-conferida-{r.ramo}-v1",
            version="1.0.0",
            logins=(HttpLogin(name="usuario", path="/login", form={"login": r.login_a, "senha": r.senha_a}),),
            checks=(
                HttpCheck(
                    id="pacote-legitimo-aplicado",
                    description="O pacote assinado pelo fornecedor continua sendo aplicado.",
                    path="/pacotes",
                    method="POST",
                    as_user="usuario",
                    multipart=envio("pacote.json", legitimo),
                    contains=("aplicado",),
                ),
                HttpCheck(
                    id="pacote-adulterado-recusado",
                    description="Um pacote alterado depois de assinado é recusado.",
                    path="/pacotes",
                    method="POST",
                    as_user="usuario",
                    multipart=envio("pacote.json", adulterado),
                    expect_status=None,
                    expect_status_in=(400, 403, 422),
                ),
                HttpCheck(
                    id="pacote-sem-assinatura-recusado",
                    description="Um pacote sem assinatura é recusado.",
                    path="/pacotes",
                    method="POST",
                    as_user="usuario",
                    multipart=envio("pacote.json", sem_assinatura),
                    expect_status=None,
                    expect_status_in=(400, 403, 422),
                ),
            ),
            inspections=(
                InspectCheck(
                    id="parametro-intacto",
                    description=f"O parâmetro {r.param} continua com o valor do pacote legítimo.",
                    db_path=banco,
                    query=f"SELECT nome, valor FROM parametros WHERE nome = '{r.param}'",  # noqa: S608
                    all_match=re.escape(valor_ok),
                ),
                InspectCheck(
                    id="versao-legitima-em-vigor",
                    description="A versão em vigor é a do pacote legítimo.",
                    db_path=banco,
                    query="SELECT 'versao', versao FROM pacote_atual",
                    all_match=re.escape(r.versao),
                ),
            ),
            success_feedback=(
                "Correção validada: o pacote do fornecedor é aplicado, e o pacote alterado ou sem "
                "assinatura é recusado sem tocar nos parâmetros."
            ),
            failure_feedback=(
                "Algumas verificações falharam. Confira cada item abaixo e ajuste o método importar de "
                "services/pacote_service.py: recalcule o HMAC e compare com hmac.compare_digest antes de gravar."
            ),
        ),
    )


SUITES_FAMILIAS: tuple[Suite, ...] = (
    tuple(s for r in XSS_RAMOS for s in _xss(r))
    + tuple(s for r in MASSA_RAMOS for s in _massa(r))
    + tuple(s for r in CSRF_RAMOS for s in _csrf(r))
    + tuple(s for r in SENHA_RAMOS for s in _senha(r))
    + tuple(s for r in UPLOAD_RAMOS for s in _upload(r))
    + tuple(s for r in SSRF_RAMOS for s in _ssrf(r))
    + tuple(s for r in LOGICA_RAMOS for s in _logica(r))
    + tuple(s for r in TENTATIVAS_RAMOS for s in _tentativas(r))
    + tuple(s for r in CORS_RAMOS for s in _cors(r))
    + tuple(s for r in PATH_RAMOS for s in _path(r))
    + tuple(s for r in CONFIANCA_RAMOS for s in _confianca(r))
    + tuple(s for r in AUTORIZACAO_RAMOS for s in _autorizacao(r))
    + tuple(s for r in ERROS_RAMOS for s in _erros(r))
    + tuple(s for r in LDAP_RAMOS for s in _ldap(r))
    + tuple(s for r in GRAPHQL_RAMOS for s in _graphql(r))
    + tuple(s for r in INVENTARIO_RAMOS for s in _inventario(r))
    + tuple(s for r in CONSUMO_RAMOS for s in _consumo(r))
    + tuple(s for r in RECURSOS_RAMOS for s in _recursos(r))
    + tuple(s for r in AUDITORIA_RAMOS for s in _auditoria(r))
    + tuple(s for r in COMPONENTE_RAMOS for s in _componente(r))
    + tuple(s for r in PACOTE_RAMOS for s in _pacote(r))
    + tuple(
        s
        for r in MOB_RAMOS
        for fn in (
            _mob_chave,
            _mob_dados_locais,
            _mob_biometria,
            _mob_logout,
            _mob_dados_demais,
            _mob_modo_teste,
        )
        for s in fn(r)
    )
)
