# Infraestrutura local (desenvolvimento)

Somente componentes **confiáveis**: PostgreSQL. Duas opções:

- `scripts/dev-db.sh start` — cluster descartável sem Docker (127.0.0.1:54329).
- `POSTGRES_PASSWORD=... docker compose -f infrastructure/local/docker-compose.yml up -d`.

O runtime de laboratórios em desenvolvimento é o `FakeRuntimeAdapter` (não executa contêineres).
