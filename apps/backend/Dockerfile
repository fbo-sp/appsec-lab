# Imagem do plano de controle (API, worker e gateway). Componente CONFIÁVEL: não contém laboratórios.
# Build a partir da raiz do repositório:  docker build -f apps/backend/Dockerfile .

# Interface web (portal + workspace) compilada em estágio separado; só os estáticos vão para a imagem.
FROM node:22-slim AS web
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web/ ./
RUN npm run build

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
COPY --from=web /web/dist /opt/web
ENV WEB_DIST_DIR=/opt/web
RUN useradd --system --uid 10001 --no-create-home appsec && chown -R appsec /src/apps/backend
USER 10001
WORKDIR /src/apps/backend
EXPOSE 8000 8001 8002
CMD ["uvicorn", "--factory", "app.main:app_factory", "--host", "0.0.0.0", "--port", "8000"]
