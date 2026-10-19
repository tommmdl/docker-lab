#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if ! docker compose version >/dev/null 2>&1; then
  export DOCKER_CONFIG="$PWD/.local/docker"
fi
# An existing Debian volume requires an explicit logical migration first.
if [[ " ${*} " == *" up "* && -z "${COMPOSE_FILE:-}" && " ${*} " != *" -f "* && "${COMPOSE_PROJECT_NAME:-docker-lab}" == docker-lab ]]; then
  current_volume=$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}{{end}}{{end}}' docker-lab-db-1 2>/dev/null || true)
  if [[ "$current_volume" == docker-lab_pgdata ]]; then
    echo 'Existing Debian database: follow docs/postgres-adoption.md before starting Alpine.' >&2
    exit 1
  fi
fi
exec docker compose "$@"
