FROM golang:1.25.12-alpine3.23 AS builder

WORKDIR /src

COPY go.mod ./
RUN go mod download

COPY cmd/ ./cmd/

RUN CGO_ENABLED=0 GOOS=linux \
    go build \
    -trimpath \
    -ldflags="-s -w" \
    -o /out/server \
    ./cmd/api


FROM scratch

ARG APP_VERSION=dev

ENV APP_VERSION=${APP_VERSION} \
    APP_PORT=8080

COPY --from=builder /out/server /server

USER 10001:10001

EXPOSE 8080

ENTRYPOINT ["/server"]
