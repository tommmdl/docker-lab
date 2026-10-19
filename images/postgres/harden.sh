#!/usr/bin/env bash
set -euo pipefail
# This image is deliberately scoped to the notes lab.
: "${POSTGRES_DB:=notes}"
: "${POSTGRES_USER:=lab}"
[[ "$POSTGRES_USER" == lab && "$POSTGRES_DB" == notes ]] || { echo 'Expected notes/lab configuration' >&2; exit 1; }
export PGHOST=/var/run/postgresql
admin=notes_admin
if ! psql -U "$admin" -d notes -Atqc 'SELECT 1' >/dev/null 2>&1; then
  admin=lab
fi
psql -U "$admin" -d notes -v ON_ERROR_STOP=1 <<'SQL'
DO $body$
BEGIN
  IF EXISTS (SELECT FROM pg_roles WHERE rolname='notes_admin') THEN
    IF shobj_description((SELECT oid FROM pg_roles WHERE rolname='notes_admin'),'pg_authid') IS DISTINCT FROM 'docker-lab local maintenance role' THEN
      RAISE EXCEPTION 'Refusing to change an unmanaged notes_admin role';
    END IF;
  ELSE
    CREATE ROLE notes_admin LOGIN SUPERUSER PASSWORD NULL;
    COMMENT ON ROLE notes_admin IS 'docker-lab local maintenance role';
  END IF;
END
$body$;
SQL
# Put rejection before the upstream loopback trust rules. Cover replication too.
rule='host all notes_admin,notes_bootstrap all reject'
if ! grep -Fxq "$rule" "$PGDATA/pg_hba.conf"; then
  temporary=$(mktemp "$PGDATA/pg_hba.conf.XXXXXX")
  printf '%s\n' "$rule" 'host replication notes_admin,notes_bootstrap all reject' > "$temporary"
  cat "$PGDATA/pg_hba.conf" >> "$temporary"
  mv "$temporary" "$PGDATA/pg_hba.conf"
fi
psql -U notes_admin -d notes -v ON_ERROR_STOP=1 <<'SQL'
SELECT pg_reload_conf();
SELECT ((SELECT oid FROM pg_roles WHERE rolname='lab')=10) AS migrate_bootstrap \gset
-- PostgreSQL requires OID 10 to remain a superuser. Preserve it separately.
DO $body$
DECLARE verifier text;
BEGIN
  IF (SELECT oid FROM pg_roles WHERE rolname='lab') = 10 THEN
    IF EXISTS (SELECT FROM pg_roles WHERE rolname='notes_bootstrap') THEN
      RAISE EXCEPTION 'notes_bootstrap already exists; refusing bootstrap migration';
    END IF;
    SELECT rolpassword INTO verifier FROM pg_authid WHERE rolname='lab';
    IF verifier IS NULL THEN RAISE EXCEPTION 'Application password is not set'; END IF;
    ALTER ROLE lab RENAME TO notes_bootstrap;
    ALTER ROLE notes_bootstrap PASSWORD NULL;
    EXECUTE format('CREATE ROLE lab LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD %L',verifier);
    ALTER DATABASE notes OWNER TO lab;
    IF to_regclass('public.notes') IS NOT NULL THEN
      ALTER TABLE public.notes OWNER TO lab;
    END IF;
  ELSE
    ALTER ROLE lab NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
  END IF;
END
$body$;
\if :migrate_bootstrap
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE usesysid=10 AND backend_type='client backend' AND pid<>pg_backend_pid();
\endif
ALTER ROLE lab SET statement_timeout = '5s';
ALTER ROLE lab SET idle_in_transaction_session_timeout = '10s';
SQL
printf '%s\n' 'Lab role hardened; maintenance uses the container Unix socket.'
