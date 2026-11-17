"""Camada de controle: a loja de pontos do [[app_nome]] e o resgate de produtos."""

from flask import Blueprint, current_app, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.produto_repository import ProdutoRepository
from services.loja_service import LojaService

painel_bp = Blueprint("painel", __name__)


def _mostrar(conexao, resultado=None, erro=None):
    conta = ContaRepository(conexao).buscar(session["usuario_id"])
    produtos = ProdutoRepository(conexao).listar()
    return render_template("painel.html", conta=conta, produtos=produtos, resultado=resultado, erro=erro)


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        return _mostrar(conexao)


@painel_bp.post("/resgatar")
@login_obrigatorio
def resgatar():
    try:
        produto_id = int(request.form.get("produto_id", ""))
        custo = int(request.form.get("custo", ""))
    except ValueError:
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            return _mostrar(conexao, erro="Pedido inválido.")
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = LojaService(ContaRepository(conexao), ProdutoRepository(conexao))
        try:
            novo = servico.resgatar(session["usuario_id"], produto_id, custo)
        except ValueError as erro:
            return _mostrar(conexao, erro=str(erro))
        return _mostrar(conexao, resultado=f"Resgate concluído. Saldo restante: {int(novo)} pontos.")
