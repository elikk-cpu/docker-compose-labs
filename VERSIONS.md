# Зафиксированные версии

Проверено: 2026-07-21.

| Назначение | Image |
|---|---|
| Nginx | `nginx:1.30.4-alpine3.24` |
| Python runtime | `python:3.13.14-slim-bookworm` |
| Go builder | `golang:1.24.13-alpine3.23` |
| Minimal runtime | `alpine:3.22.2` |
| PostgreSQL | `postgres:17.10-alpine3.23` |
| Redis | `redis:8.6.4-alpine3.23` |
| RabbitMQ | `rabbitmq:4.3.1-management-alpine` |
| Registry | `registry:3` |
| Prometheus | `prom/prometheus:v3.4.0` |
| Grafana | `grafana/grafana:12.2.10-ubuntu` |
| Диагностический curl | `curlimages/curl:8.12.1` |

Версии намеренно зафиксированы. Если конкретный tag станет недоступен, выбери
существующий конкретный patch-tag той же ветки, обнови этот файл и объясни изменение
в commit message. Не заменяй tag на `latest`.
