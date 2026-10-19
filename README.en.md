# Docker: an app, a database and a few failures

English · [Português](README.md)

## Current database: Alpine, with a tested rollback

The labs now use the tested PostgreSQL Alpine image by digest. Adoption used logical backups and new volumes; original Debian volumes are retained. Actual API rollback preserved a note written after cutover. Read the [migration, backup and recovery procedure](docs/postgres-adoption.en.md). Earlier security reports remain available.

A notes app is small enough to keep the focus on the infrastructure around it. Here, the API and PostgreSQL run in separate containers, connected through Compose.

The interesting questions appear when containers are recreated or the database stops: are the notes still there? Can the API report that it is not ready? Does it recover when the database returns?

## Getting started

Linux/WSL, Docker, Bash, Python 3, curl and an available port 8000. Preparation can install Compose locally on Linux x86_64.

From the repository root:

```bash
bash scripts/prepare.sh
bash scripts/compose.sh up -d --build --wait --wait-timeout 180
```

Open http://localhost:8000 and create a note. The selector at the top switches between Portuguese and English.

## Things to try

1. Create, list and delete notes through the UI or API.
2. Recreate the containers and see what the volume preserved.
3. Stop the database and compare `/healthz` with `/readyz`.
4. Start the database again and watch the API recover.

## What has been tested

All 23 integration checks passed. They cover persistence after container recreation, 503 responses during a database outage and recovery without restarting the API.

The [results and their limits](docs/validation.en.md) include execution details and evidence. They refer to the revisions recorded in those reports.

## When you are done

```bash
bash scripts/compose.sh down
```

The notes remain in the volume. Adding `-v` deletes them. The API binds only to localhost and has no user authentication; this is a learning environment.

## A closer look

The [usage guide](docs/guide.en.md) covers architecture, configuration, tests, limitations and troubleshooting. The [portfolio](https://github.com/tommmdl/devops-portfolio) connects this project to the other labs.

[About the history update](docs/history.md)

Read about the [image updates and remaining findings](docs/remediation.en.md).

Remediation validation: 23 Compose checks, a controlled restore of three notes from the original PostgreSQL image into the rebuilt image, and 19 local tracing checks. The running Argo CD application is Synced/Healthy and retains the same PVC. Full evidence and remaining issues are linked above.

The [PostgreSQL critical-finding review and hardening](docs/database-hardening.en.md) explains the smaller image, application/maintenance roles and the checks for existing volumes.

The [Alpine PostgreSQL alternative](docs/postgres-alternative.en.md) tests a fixed libxml2 in a separate volume, with logical restore and rollback checks. That test was followed by the adoption documented above.
