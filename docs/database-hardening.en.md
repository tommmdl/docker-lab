# A smaller database image and a separate application role

[Português](database-hardening.md) · English

The critical-finding review removes libsqlite3-0 together with unused GPG key-management tools. PostgreSQL does not link to SQLite, and apt's dependency simulation leaves the server/client packages intact. gpgv and the Debian archive keyrings remain for package signature verification. This is package removal, not a scanner exception.

The application still connects as `lab` with the same password, but it no longer receives a superuser account. PostgreSQL requires the bootstrap role (OID 10) to stay a superuser. On first initialization or explicit upgrade, `lab-db-harden` renames that role to `notes_bootstrap`, clears its password, creates a new ordinary `lab` role with the existing password verifier, and assigns the notes database/table to it. Existing identity-sequence ownership follows the table. The script does not reassign system catalog ownership.

`notes_admin` is the local maintenance role, has no password, and is explicitly rejected over TCP alongside `notes_bootstrap`, including loopback and replication connections. Local Unix-socket administration still trusts users inside the database container. Container/host access remains an administrative boundary. The application remains the owner of its database/table so the existing lab migrations work; this is not a strict DML-only role.

Compose limits the database to 384 MiB, one CPU and 256 PIDs, sets no-new-privileges and keeps the database port unpublished. Role defaults add a 5-second statement timeout and a 10-second idle transaction timeout. These reduce privileges and constrain resource use; they do not patch libxml2 or disable XML parsing. SQL users can change those session defaults. The two remaining critical findings still block the security gate.

## Fresh and existing databases

Fresh databases run the hardening hook during the official entrypoint initialization. Changing an image does not rerun initialization hooks on existing volumes.

For an existing instance, first save a private data backup, globals backup and pg_hba.conf. After switching to the tested database image, apply the explicit migration:

```bash
bash scripts/compose.sh exec -T --user postgres db lab-db-harden
```

This operation is scoped to `notes`/`lab`; it refuses other configurations. It retains the app login, transfers only the known lab ownership and disconnects old bootstrap client sessions during the first migration. Use a maintenance window. Do not use it as a generic shared-cluster migration.

For maintenance afterward:

```bash
bash scripts/compose.sh exec -T --user postgres db psql -U notes_admin -d notes
```

Rolling back the image does not undo persistent roles or pg_hba.conf. Keep the local maintenance role and use the saved backups for a deliberate recovery; avoid blindly restoring globals over the running cluster.

## Repeat the checks

```bash
python3 tests/database_security.py
python3 tests/integration.py
python3 tests/database_upgrade.py
```

The 20 security checks exercise privilege denials, TCP admin rejection, timeouts, literal XML-looking note text and resource limits. A benign SQL XML parse is expected to succeed: that records residual exposure. The 23 integration checks keep covering API behavior and persistence. The upgrade test starts a separate original-image database with three notes, upgrades the same volume, migrates roles, checks old privileged-session termination and verifies every note field. It removes only its own temporary project and volume.

Full findings, vendor sources and before/after scans: [security-lab](https://github.com/tommmdl/security-lab/blob/main/docs/postgresql-critical.en.md).
