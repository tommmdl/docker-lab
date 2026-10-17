# Validation — 2026-10-17

[Português](validation.md)

Actual execution on Linux/WSL with Docker Engine 29.1.3 and Compose 5.6.0. All 23 checks completed at 18:53:48 America/Sao_Paulo (21:53:48 UTC). Execution performed by the assistant with owner authorization.

## Results

| Scenario | Observed result |
| --- | --- |
| Compose startup | API and database healthy |
| Web page | HTML served with Portuguese and English strings |
| API | Create, list and delete notes; 404 for missing ID deletion |
| Validation | 400 for invalid titles; 413 for oversized body |
| Parameterized SQL | SQL-like text stored literally; table preserved |
| Container recreation | Note preserved in the volume |
| Database stopped | Liveness 200; readiness and listing 503 |
| Database restarted | API recovered without restarting |
| Test cleanup | Test-created notes deleted |
| Runtime configuration | API UID 10001, read-only rootfs; database port unpublished |

## Evidence

- [Results of all 23 checks](../evidence/integration-results.json)
- [Versions and selected container properties](../evidence/runtime.json)
- [Application logs covering outage and recovery](../evidence/api.log)
- [Test implementation](../tests/integration.py)

Python 3.13.16, Flask 3.1.2, Gunicorn 23.0.0, Psycopg 3.3.6 and PostgreSQL 17.11. Base images pinned by digest and Python dependencies pinned in `requirements.lock`. Local secrets were excluded from published files.

## Limits

The page was checked over HTTP without visual verification or automated browser clicks. Tests cover a controlled outage and volume persistence, not load, volume loss, backup/restore, TLS or authentication. SQL-like input is a focused parameterization check, not a full security audit. Containers remain running for local exploration. The separate Jenkins lab was not modified.

This managed environment requires authorized Docker commands outside the sandbox. The previously verified official Compose binary was reused locally; on a fresh clone, `prepare.sh` installs it with checksum verification if needed. Buildx was absent, so Docker used the classic builder.
