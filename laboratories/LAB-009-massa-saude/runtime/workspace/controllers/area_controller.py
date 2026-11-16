"""Camada de controle: Auditoria médica, só para o perfil "auditor"."""

from flask import Blueprint, abort, current_app, render_template

from controllers.auth_controller import login_obrigatorio, usuario_atual
from database.conexao import abrir_conexao
from repositories.usuario_repository import UsuarioRepository

area_bp = Blueprint("area", __name__)


@area_bp.get("/auditoria")
@login_obrigatorio
def listar():
    usuario = usuario_atual()
    if usuario is None or not usuario.eh_privilegiado:
        abort(403)
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        repositorio = UsuarioRepository(conexao)
        usuarios = repositorio.listar_todos()
        chave = repositorio.buscar_parametro("senha_liberacao_dia")
    return render_template("area.html", usuarios=usuarios, chave=chave)
