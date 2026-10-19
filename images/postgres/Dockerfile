# Keep PostgreSQL 17 and Bookworm; rebuild only the privilege-drop helper.
FROM golang:1.27.2-bookworm@sha256:5cf287a799e6b94384bad13d16b14904c531f51ba65792237e122ce42b392f61 AS gosu
ENV CGO_ENABLED=0 GOTOOLCHAIN=local
RUN git clone https://github.com/tianon/gosu.git /src \
    && cd /src \
    && git checkout 6456aaa0f3c854d199d0f037f068eb97515b7513 \
    && go get github.com/moby/sys/user@v0.4.1 golang.org/x/sys@v0.44.0 \
    && go mod verify \
    && go test ./... \
    && go build -trimpath -ldflags "-s -w" -o /out/gosu . \
    && go version -m /out/gosu

FROM postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826
COPY --from=gosu /out/gosu /usr/local/bin/gosu
RUN gosu nobody id && gosu postgres id && postgres --version

# Build-time key-management tools are not needed to serve this database.
RUN apt-get purge -y --auto-remove libsqlite3-0 \
    && test "$(dpkg-query -W -f='${db:Status-Status}' libsqlite3-0 2>/dev/null || true)" != installed \
    && command -v gpgv \
    && postgres --version
COPY --chmod=0755 harden.sh /usr/local/bin/lab-db-harden
COPY --chmod=0755 init-hardening.sh /docker-entrypoint-initdb.d/10-lab-hardening.sh
