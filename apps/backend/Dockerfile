# Imagem do plano de controle (API e worker). Componente CONFIÁVEL: não contém laboratórios.
# Build a partir da raiz do repositório:  docker build -f apps/backend/Dockerfile .
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir "uv==0.8.17"
WORKDIR /src
COPY pyproject.toml uv.lock ./
COPY packages/contracts/pyproject.toml packages/contracts/pyproject.toml
COPY apps/backend/pyproject.toml apps/backend/pyproject.toml
COPY packages/contracts/src packages/contracts/src
COPY apps/backend/app apps/backend/app
RUN uv sync --frozen --no-dev --no-editable --all-packages --all-extras
COPY apps/backend/alembic.ini apps/backend/alembic.ini
COPY apps/backend/migrations apps/backend/migrations
COPY laboratories laboratories
RUN useradd --system --uid 10001 --no-create-home appsec && chown -R appsec /src/apps/backend
USER 10001
WORKDIR /src/apps/backend
EXPOSE 8000
CMD ["uvicorn", "--factory", "app.main:app_factory", "--host", "0.0.0.0", "--port", "8000"]
