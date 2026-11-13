"""Camada de controle: recebe a requisição HTTP, chama o serviço e escolhe a página de resposta."""

from flask import Blueprint, current_app, render_template, request

from database.conexao import abrir_conexao
from repositories.medico_repository import MedicoRepository
from services.medico_service import MedicoService

medicos_bp = Blueprint("medicos", __name__)


@medicos_bp.route("/medicos", methods=["GET", "POST"])
def buscar():
    termo = request.values.get("nome", "")
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = MedicoService(MedicoRepository(conexao), current_app.config["TAMANHO_MAXIMO_BUSCA"])
        medicos = servico.buscar(termo)
    return render_template("medicos.html", termo=termo, medicos=medicos)
