# Reuse only the static, already-remediated helper; Debian libraries stay out.
FROM ghcr.io/tommmdl/docker-lab@sha256:be42c09595d7059956490eeab607b742afc96268db48f91f4eb1fd53edc89b52 AS helper
FROM postgres:17.11-alpine3.24@sha256:b0f9560a2de083e2cc7382e75f808c7381a32852a7ec49117deedb300e552b24
COPY --from=helper /usr/local/bin/gosu /usr/local/bin/gosu
COPY --chmod=0755 images/postgres/harden.sh /usr/local/bin/lab-db-harden
COPY --chmod=0755 images/postgres/init-hardening.sh /docker-entrypoint-initdb.d/10-lab-hardening.sh
RUN apk add --no-cache zlib=1.3.2-r1
RUN gosu nobody id && gosu postgres id && postgres --version
