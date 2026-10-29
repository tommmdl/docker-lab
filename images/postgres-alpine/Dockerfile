# Build the static privilege-drop helper here; the retained Debian image keeps its older toolchain.
FROM golang:1.27.3-bookworm@sha256:d9b6a1beb9474adc2a1ce842573639b44b2a0dd49b6669f51d3821baf9ec37c9 AS gosu
ENV CGO_ENABLED=0 GOTOOLCHAIN=local
RUN git clone https://github.com/tianon/gosu.git /src \
    && cd /src \
    && git checkout 6456aaa0f3c854d199d0f037f068eb97515b7513 \
    && go get github.com/moby/sys/user@v0.4.1 golang.org/x/sys@v0.44.0 \
    && go mod verify \
    && go test ./... \
    && go build -trimpath -ldflags "-s -w" -o /out/gosu . \
    && go version -m /out/gosu

FROM postgres:17.11-alpine3.24@sha256:b0f9560a2de083e2cc7382e75f808c7381a32852a7ec49117deedb300e552b24
COPY --from=gosu /out/gosu /usr/local/bin/gosu
COPY --chmod=0755 images/postgres/harden.sh /usr/local/bin/lab-db-harden
COPY --chmod=0755 images/postgres/init-hardening.sh /docker-entrypoint-initdb.d/10-lab-hardening.sh
RUN apk add --no-cache zlib=1.3.2-r1
RUN gosu nobody id && gosu postgres id && postgres --version
