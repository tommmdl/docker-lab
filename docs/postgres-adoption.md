# Adotando o PostgreSQL Alpine

O banco padrão agora usa o digest Alpine testado. O [procedimento completo nos dois idiomas](https://github.com/tommmdl/security-lab/blob/main/docs/postgres-adoption.md) reúne a migração, os backups privados, o rollback testado e os achados preservados. Instalações Debian existentes precisam migrar logicamente antes de iniciar o novo padrão.

O Docker usa `docker-lab_pgdata_alpine_v1`; o original `docker-lab_pgdata` permanece guardado.
