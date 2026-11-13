"""Apoio aos testes que exigem Docker real (ADR-008). Opt-in por ``DOCKER_CONTRACT_TESTS=1``."""

from __future__ import annotations

import os
from functools import cache
from pathlib import Path

import pytest

LABS = Path(__file__).resolve().parents[3] / "laboratories"
LAB000_RUNTIME = LABS / "LAB-000-hello-benign" / "runtime"
BASE_PYTHON = LABS / "_base" / "python"
LOCAL_TAG = "cecyber-labs/lab-000-hello:local"


def docker_enabled() -> bool:
    return os.environ.get("DOCKER_CONTRACT_TESTS") == "1"


@cache
def _build() -> str:
    import docker

    client = docker.from_env()
    # SKIP_BASE_BUILD=1 reaproveita a base já construída (ex.: ambientes atrás de proxy com CA própria).
    if os.environ.get("SKIP_BASE_BUILD") != "1":
        client.images.build(path=str(BASE_PYTHON), tag="cecyber-labs/base-python:local", rm=True)
    image, _ = client.images.build(path=str(LAB000_RUNTIME), tag=LOCAL_TAG, rm=True)
    return f"local/labs/lab-000-hello@{image.id}"


LAB001_RUNTIME = LABS / "LAB-001-sqli-clinica" / "runtime"
LAB001_TAG = "cecyber-labs/lab-001-sqli:local"


@cache
def _build_lab001() -> str:
    import docker

    client = docker.from_env()
    _build()  # garante a base
    # SKIP_LAB_BUILD=1 usa a imagem já construída (ex.: build com CA de proxy, fora do repositório).
    if os.environ.get("SKIP_LAB_BUILD") == "1":
        image = client.images.get(LAB001_TAG)
    else:
        image, _ = client.images.build(path=str(LAB001_RUNTIME), tag=LAB001_TAG, rm=True)
    return f"local/labs/lab-001-sqli@{image.id}"


def lab001_image() -> str:
    """Imagem do LAB-001 (vulnerabilidade INTENCIONAL; só em rede interna da sessão)."""
    docker_lab_image()  # mesmas condições de opt-in e disponibilidade
    return _build_lab001()


def docker_lab_image() -> str:
    """Constrói (com cache) a imagem do LAB-000 e devolve a referência por digest do ID local."""
    if not docker_enabled():
        pytest.skip("DOCKER_CONTRACT_TESTS != 1: testes com Docker real não executados")
    try:
        import docker

        docker.from_env().ping()
    except Exception as exc:  # pragma: no cover - depende do ambiente
        pytest.skip(f"Docker indisponível: {exc}")
    return _build()
