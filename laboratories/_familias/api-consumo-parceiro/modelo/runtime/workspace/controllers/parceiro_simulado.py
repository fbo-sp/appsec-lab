"""SIMULAÇÃO do [[parceiro_nome]] (só existe no laboratório).

Num sistema real, esta API fica fora da empresa, mantida pelo parceiro. Aqui ela roda no mesmo
contêiner, sem internet, e tem um interruptor de "modo comprometido" que imita o parceiro invadido:
a resposta passa a trazer valores absurdos e um campo que não existe no contrato. Você NÃO precisa
mexer neste arquivo: a correção é no lado de quem consome a API (services/consulta_service.py).
"""

from pathlib import Path

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for

parceiro_bp = Blueprint("parceiro", __name__)

# Respostas normais do parceiro, por referência (dados fictícios).
NORMAIS = [[py:respostas_normais]]


def _comprometido() -> bool:
    arquivo = Path(current_app.config["ARQUIVO_MODO_PARCEIRO"])
    return arquivo.exists() and arquivo.read_text().strip() == "comprometido"


@parceiro_bp.get("/parceiro/api/consulta/<referencia>")
def consulta(referencia: str):
    if referencia not in NORMAIS:
        return jsonify({"erro": "referência desconhecida"}), 404
    if _comprometido():
        return jsonify({"referencia": referencia, "[[campo]]": [[valor_comprometido]], "aprovacao_automatica": True})
    return jsonify({"referencia": referencia, "[[campo]]": NORMAIS[referencia]})


@parceiro_bp.get("/parceiro/admin")
def admin():
    return render_template("parceiro_admin.html", comprometido=_comprometido())


@parceiro_bp.post("/parceiro/admin/modo")
def mudar_modo():
    modo = "comprometido" if request.form.get("modo") == "comprometido" else "normal"
    Path(current_app.config["ARQUIVO_MODO_PARCEIRO"]).write_text(modo)
    return redirect(url_for("parceiro.admin"))
