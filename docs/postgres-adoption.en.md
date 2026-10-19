# Adopting PostgreSQL Alpine

The default database now uses the tested Alpine digest. Follow the [complete bilingual procedure](https://github.com/tommmdl/security-lab/blob/main/docs/postgres-adoption.en.md) for the migration, private backups, tested rollback and retained findings. Existing Debian installations must migrate logically before starting the new default.

Docker uses `docker-lab_pgdata_alpine_v1`; the original `docker-lab_pgdata` is retained.
