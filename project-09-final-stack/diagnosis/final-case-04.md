# Broken scenario 04 — Healthcheck checks the wrong endpoint

## Symptom

Backend-процесс работал, но контейнер получил состояние:

```text
status=running health=unhealthy
```

Frontend не мог стартовать, потому что зависел от healthy backend.

## Команды диагностики

```bash
docker compose   -p final-broken-04   -f compose.yaml   -f compose.prod.yaml   -f broken/case-04/compose.broken.yaml   ps -a

docker inspect <backend-container>

docker inspect <backend-container>   --format '{{range .State.Health.Log}}{{println .ExitCode}}{{println .Output}}{{end}}'

docker exec <backend-container>   python -c "..."
```

## Evidence

Healthcheck обращался к:

```text
http://127.0.0.1:8000/wrong-endpoint
```

Ответ:

```text
HTTP 404 Not Found
```

При этом реальные endpoints работали:

```text
/healthz -> {"status":"alive"}
/readyz  -> {"status":"ready"}
```

## Root cause

Healthcheck проверял несуществующий endpoint.

Главный процесс backend продолжал работать, поэтому container status оставался `running`.

Healthcheck завершался с exit code `1`, поэтому health status становился `unhealthy`.

## Минимальное исправление

Было:

```yaml
healthcheck:
  test:
    - CMD
    - python
    - -c
    - import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/wrong-endpoint', timeout=2)
```

Стало:

```yaml
healthcheck:
  test:
    - CMD
    - python
    - -c
    - import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=2)
```

## Проверка исправления

```bash
FRONTEND_PORT=8184 docker compose   -p final-broken-04   -f compose.yaml   -f compose.prod.yaml   -f broken/case-04/compose.fixed.yaml   up -d --wait
```

После исправления:

```text
status=running health=healthy
```

Все core-сервисы стали healthy.

## Почему restart или prune не является исправлением

Restart снова запускал бы тот же healthcheck с `/wrong-endpoint`.

Контейнер снова стал бы `unhealthy`.

Prune не изменил бы healthcheck в Compose-конфигурации.

Root cause устраняется заменой неверного endpoint на readiness endpoint `/readyz`.
