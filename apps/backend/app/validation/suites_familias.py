"""Suítes PROTEGIDAS das famílias de laboratórios por ramo (ADR-021).

Uma família tem a mesma mecânica em vários ramos de atividade; aqui cada família tem uma função que
monta as suítes de um ramo a partir dos dados fictícios desse ramo (rotas, logins, respostas). Os mesmos
valores aparecem no seed de cada lab (``laboratories/_familias/<familia>/ramos.yaml``); os testes Docker
de cada família conferem os dois lados.
"""

from __future__ import annotations

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


SUITES_FAMILIAS: tuple[Suite, ...] = (
    tuple(s for r in XSS_RAMOS for s in _xss(r))
    + tuple(s for r in MASSA_RAMOS for s in _massa(r))
    + tuple(s for r in CSRF_RAMOS for s in _csrf(r))
    + tuple(s for r in SENHA_RAMOS for s in _senha(r))
    + tuple(s for r in UPLOAD_RAMOS for s in _upload(r))
    + tuple(s for r in SSRF_RAMOS for s in _ssrf(r))
    + tuple(s for r in LOGICA_RAMOS for s in _logica(r))
    + tuple(s for r in TENTATIVAS_RAMOS for s in _tentativas(r))
)
