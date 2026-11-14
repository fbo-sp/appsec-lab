"""Camada de controle: página de diagnóstico de comunicação com os CLPs."""

from flask import Blueprint, current_app, render_template, request

from infra.executor_comandos import ExecutorComandos
from repositories.equipamento_repository import EquipamentoRepository
from services.diagnostico_service import DiagnosticoService

diagnostico_bp = Blueprint("diagnostico", __name__)


@diagnostico_bp.route("/diagnostico", methods=["GET", "POST"])
def testar():
    equipamentos = EquipamentoRepository(current_app.config["INVENTARIO_CLPS"]).listar()
    endereco = request.form.get("endereco", "")
    relatorio = None
    if request.method == "POST":
        servico = DiagnosticoService(ExecutorComandos(current_app.config["TEMPO_LIMITE_DIAGNOSTICO"]))
        relatorio = servico.testar_comunicacao(endereco)
    return render_template(
        "diagnostico.html", equipamentos=equipamentos, endereco=endereco, relatorio=relatorio
    )
