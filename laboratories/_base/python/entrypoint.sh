#!/bin/sh
# Inicia o agente de workspace em segundo plano e executa o comando de startup do manifesto.
/opt/agent/bin/python /opt/agent/agent.py &
exec "$@"
