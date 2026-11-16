"""Suítes PROTEGIDAS das famílias de laboratórios por ramo (ADR-021).

Uma família tem a mesma mecânica em vários ramos de atividade; aqui cada família tem uma função que
monta as suítes de um ramo a partir dos dados fictícios desse ramo (rotas, logins, respostas). Os mesmos
valores aparecem no seed de cada lab (``laboratories/_familias/<familia>/ramos.yaml``); os testes Docker
de cada família conferem os dois lados.
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass

from app.validation.suites import AnswerSuite, HttpCheck, HttpLogin, HttpSuite, Suite

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


SUITES_FAMILIAS: tuple[Suite, ...] = tuple(s for r in XSS_RAMOS for s in _xss(r))
