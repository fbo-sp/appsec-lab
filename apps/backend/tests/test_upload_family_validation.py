"""Suíte da família upload (LAB-014..016) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa aprovar validação por assinatura do conteúdo + nome gerado + nosniff no download, e
reprovar o código original, uma correção só com a assinatura (sem nosniff) e uma correção só com o
nosniff (sem validar o conteúdo, que segue aceitando o HTML forjado).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import UPLOAD_RAMOS, UploadRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-014-upload-cooperativa", "lab-014-upload"),
    "sau": ("LAB-015-upload-clinica", "lab-015-upload"),
    "ind": ("LAB-016-upload-fornecedores", "lab-016-upload"),
}
SERVICO = "/workspace/services/anexo_service.py"
CONTROLLER = "/workspace/controllers/anexo_controller.py"

IMPORT = (
    "import logging\n"
    "import os\n\n"
    "from werkzeug.datastructures import FileStorage\n"
    "from werkzeug.utils import secure_filename\n"
)
IMPORT_NOVO = "import logging\nimport os\nimport uuid\n\nfrom werkzeug.datastructures import FileStorage\n"
SALVAR = (
    "    def salvar(self, dono_id: int, descricao: str, arquivo: FileStorage | None) -> str:\n"
    '        """Confere o tipo, grava o arquivo em /tmp/anexos e registra o envio. Devolve o nome gravado."""\n'
    "        if arquivo is None or not arquivo.filename:\n"
    '            raise ValueError("Escolha um arquivo para enviar.")\n'
    "        # O navegador informa o tipo do arquivo (Content-Type) junto com o envio.\n"
    "        if arquivo.mimetype not in Config.TIPOS_PERMITIDOS:\n"
    '            raise ValueError("Envie um PDF, PNG ou JPEG.")\n'
    '        nome = secure_filename(arquivo.filename)  # tira barras e "..": o arquivo não sai da pasta\n'
    "        arquivo.save(os.path.join(Config.PASTA_ANEXOS, nome))\n"
    "        self._repositorio.inserir(dono_id, descricao.strip()[:120], nome)\n"
    '        logger.info("Anexo recebido: dono=%s arquivo=%s tipo_informado=%s", dono_id, nome, arquivo.mimetype)\n'
    "        return nome\n"
)
SALVAR_NOVO = (
    '    ASSINATURAS = {b"%PDF-": ".pdf", b"\\x89PNG\\r\\n\\x1a\\n": ".png", b"\\xff\\xd8\\xff": ".jpg"}\n\n'
    "    def salvar(self, dono_id: int, descricao: str, arquivo: FileStorage | None) -> str:\n"
    '        """Confere o conteúdo, grava com nome próprio e registra o envio. Devolve o nome gravado."""\n'
    "        if arquivo is None or not arquivo.filename:\n"
    '            raise ValueError("Escolha um arquivo para enviar.")\n'
    "        cabecalho = arquivo.stream.read(8)\n"
    "        arquivo.stream.seek(0)\n"
    "        extensao = next((e for assinatura, e in self.ASSINATURAS.items() if cabecalho.startswith(assinatura)), None)\n"
    "        if extensao is None:\n"
    '            raise ValueError("Envie um PDF, PNG ou JPEG de verdade.")\n'
    "        nome = uuid.uuid4().hex + extensao\n"
    "        arquivo.save(os.path.join(Config.PASTA_ANEXOS, nome))\n"
    "        self._repositorio.inserir(dono_id, descricao.strip()[:120], nome)\n"
    '        logger.info("Anexo recebido: dono=%s arquivo=%s", dono_id, nome)\n'
    "        return nome\n"
)
BAIXAR = (
    "def baixar(nome: str):\n"
    '    """Mostra o arquivo no navegador. O Content-Type vem da extensão do nome."""\n'
    "    return send_from_directory(Config.PASTA_ANEXOS, nome)\n"
)
BAIXAR_NOVO = (
    "def baixar(nome: str):\n"
    '    """Entrega o arquivo guardado, sem deixar o navegador adivinhar o tipo."""\n'
    "    resposta = send_from_directory(Config.PASTA_ANEXOS, nome)\n"
    '    resposta.headers["X-Content-Type-Options"] = "nosniff"\n'
    "    return resposta\n"
)


@pytest.fixture(scope="module")
def runtime() -> Iterator[tuple[Any, Any]]:
    docker_lab_image()  # pula sem DOCKER_CONTRACT_TESTS=1 antes de tocar no Docker
    from app.runtime.docker_local import DockerRuntimeAdapter
    from app.validation.docker_eval import DockerEvaluator

    rt = DockerRuntimeAdapter()
    before = {owned.runtime_ref for owned in rt.list_owned()}
    try:
        yield rt, DockerEvaluator()
    finally:
        for owned in rt.list_owned():
            if owned.runtime_ref not in before:
                rt.terminate(owned.runtime_ref)


def _lab(ramo: str) -> LabUnderTest:
    lab_dir, name = LABS[ramo]
    return LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))


def _corrigir_servico(box: Any) -> None:
    replace_in_file(box, SERVICO, IMPORT, IMPORT_NOVO)
    replace_in_file(box, SERVICO, SALVAR, SALVAR_NOVO)


def _corrigir_controller(box: Any) -> None:
    replace_in_file(box, CONTROLLER, BAIXAR, BAIXAR_NOVO)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_accepts_forged_html_and_serves_it(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    assert r["pdf-legitimo-aceito"], r
    assert not r["html-forjado-recusado"], r
    assert not r["download-sem-sniff"], r
    assert not r["sem-html-armazenado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_signature_name_and_nosniff_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    _corrigir_servico(box)
    _corrigir_controller(box)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_signature_without_nosniff_is_rejected(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    _corrigir_servico(box)  # valida o conteúdo, mas não acrescenta o nosniff no download
    r = lab.evaluate(ev, ref)
    assert r["html-forjado-recusado"] and r["sem-html-armazenado"], r
    assert not r["download-sem-sniff"], r


def test_nosniff_without_content_validation_is_rejected(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("ind")
    box, ref = lab.provision(rt)
    _corrigir_controller(box)  # acrescenta o nosniff, mas segue aceitando pelo Content-Type
    r = lab.evaluate(ev, ref)
    assert r["download-sem-sniff"], r
    assert not r["html-forjado-recusado"] and not r["sem-html-armazenado"], r


@pytest.mark.parametrize("r", UPLOAD_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: UploadRamo) -> None:
    expected = {
        f"upload/answer/campo-checado-{r.ramo}-v1": "mimetype",
        f"upload/answer/caminho-servido-{r.ramo}-v1": "/anexos/comprovante.html",
        f"upload/answer/tipo-servido-{r.ramo}-v1": "text/html",
        f"upload/answer/assinatura-pdf-{r.ramo}-v1": "%PDF",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
