"""Erros de API no envelope de docs/13_API_SPEC.md §5."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.logging import correlation_id_var


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}


def not_found(kind: str) -> ApiError:
    # 404 também para recursos existentes mas não visíveis (sem vazar metadados).
    return ApiError(404, "NOT_FOUND", f"{kind} não encontrado.")


def _envelope(status: int, code: str, message: str, details: dict[str, Any]) -> JSONResponse:
    body = {
        "error": {"code": code, "message": message, "requestId": correlation_id_var.get(), "details": details}
    }
    return JSONResponse(status_code=status, content=body)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, exc: ApiError) -> JSONResponse:
        return _envelope(exc.status, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [{"loc": ".".join(str(p) for p in e["loc"]), "message": e["msg"]} for e in exc.errors()]
        return _envelope(400, "VALIDATION_ERROR", "Requisição inválida.", {"errors": errors})

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "HTTP_ERROR")
        return _envelope(exc.status_code, code, str(exc.detail), {})
