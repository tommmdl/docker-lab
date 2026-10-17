#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if ! docker compose version >/dev/null 2>&1; then
  export DOCKER_CONFIG="$PWD/.local/docker"
fi
exec docker compose "$@"
