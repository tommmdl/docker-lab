#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
python3 - <<'PY'
from pathlib import Path
import secrets
p = Path('.local/db-password')
p.parent.mkdir(exist_ok=True)
p.parent.chmod(0o700)
if not p.exists():
    p.write_text(secrets.token_urlsafe(32))
# Local Compose secrets are bind-mounted; the non-root API UID must read the file.
# Protect host access with the parent directory rather than an owner-only file.
p.chmod(0o644)
print('Local database password ready; existing password preserved.')
PY
if ! docker compose version >/dev/null 2>&1; then
  target="$PWD/.local/docker/cli-plugins"
  mkdir -p "$target"
  if [ ! -x "$target/docker-compose" ]; then
    test "$(uname -m)" = x86_64
    base=https://github.com/docker/compose/releases/download/v5.6.0
    curl --fail --location "$base/docker-compose-linux-x86_64" -o "$target/docker-compose"
    curl --fail --location "$base/docker-compose-linux-x86_64.sha256" -o .local/compose.sha256
    python3 - <<'PY'
from pathlib import Path
import hashlib
p = Path('.local/docker/cli-plugins/docker-compose')
expected = Path('.local/compose.sha256').read_text().split()[0]
if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
    raise SystemExit('Compose checksum mismatch')
p.chmod(0o755)
PY
  fi
fi
bash scripts/compose.sh version
