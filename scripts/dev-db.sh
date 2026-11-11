#!/usr/bin/env bash
# Cluster PostgreSQL DESCARTÁVEL para desenvolvimento/testes locais, sem Docker.
# Escuta somente em 127.0.0.1 e usa autenticação "trust" restrita ao loopback: não use
# para nada além de testes locais. Uso: scripts/dev-db.sh start|stop|url
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PGDATA="${PGDATA_DIR:-$ROOT/.local-pg/data}"
PORT="${PGPORT_DEV:-54329}"
PGBIN="${PG_BIN:-$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)}"
RUN_AS=()
if [ "$(id -u)" = "0" ]; then RUN_AS=(runuser -u postgres --); fi

case "${1:-}" in
  start)
    mkdir -p "$(dirname "$PGDATA")"
    [ "$(id -u)" = "0" ] && chown -R postgres "$(dirname "$PGDATA")"
    if [ ! -f "$PGDATA/PG_VERSION" ]; then
      "${RUN_AS[@]}" "$PGBIN/initdb" -D "$PGDATA" -U appsec --auth=trust -E UTF8 >/dev/null
    fi
    if ! "${RUN_AS[@]}" "$PGBIN/pg_ctl" -D "$PGDATA" status >/dev/null 2>&1; then
    "${RUN_AS[@]}" "$PGBIN/pg_ctl" -D "$PGDATA" -o "-p $PORT -c listen_addresses=127.0.0.1 -k /tmp" -l "$PGDATA/server.log" -w start >/dev/null
    fi
    for db in appsec_labs appsec_labs_test; do
      psql -h 127.0.0.1 -p "$PORT" -U appsec -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$db'" | grep -q 1 \
        || psql -h 127.0.0.1 -p "$PORT" -U appsec -d postgres -qc "CREATE DATABASE $db"
    done
    echo "PostgreSQL local em 127.0.0.1:$PORT"
    ;;
  stop) "${RUN_AS[@]}" "$PGBIN/pg_ctl" -D "$PGDATA" -m fast stop ;;
  url) echo "postgresql+psycopg://appsec@127.0.0.1:$PORT/${2:-appsec_labs}" ;;
  *) echo "uso: $0 start|stop|url [db]" >&2; exit 2 ;;
esac
