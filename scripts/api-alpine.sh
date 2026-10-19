#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
for arg in "$@"; do
  if [[ "$arg" == --build || "$arg" == build ]]; then
    echo 'Build the Alpine Dockerfile explicitly; this preview only runs existing images.' >&2
    exit 1
  fi
done
export COMPOSE_PROJECT_NAME=notes-api-alpine-preview
export COMPOSE_FILE="$PWD/compose.yaml:$PWD/compose.api-alpine.yaml"
export API_PORT=8016
exec bash scripts/compose.sh "$@"
