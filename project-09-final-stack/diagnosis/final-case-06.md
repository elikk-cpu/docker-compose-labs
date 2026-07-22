# Broken scenario 06 — Production override returns source bind mounts

## Symptom

Production-like сервисы запускались успешно и были healthy, но исходный код с host был примонтирован внутрь контейнеров.

Backend содержал bind mount:

```text
/home/aa/docker-compose-labs/project-09-final-stack/backend/app.py
-> /app/app.py
```

Worker содержал bind mount:

```text
/home/aa/docker-compose-labs/project-09-final-stack/worker/worker.py
-> /app/worker.py
```

## Команды диагностики

```bash
docker compose   -f compose.yaml   -f compose.prod.yaml   -f broken/case-06/compose.broken.yaml   config

docker inspect final-broken-06-backend-1   --format '{{json .Mounts}}'

docker inspect final-broken-06-worker-1   --format '{{json .Mounts}}'
```

## Evidence

Итоговая Compose-конфигурация содержала targets:

```text
/app/app.py
/app/worker.py
```

Фактический `docker inspect` подтвердил bind mounts:

```text
Type=bind
Destination=/app/app.py
RW=false
```

и:

```text
Type=bind
Destination=/app/worker.py
RW=false
```

## Root cause

Production override случайно добавил bind mounts исходного кода.

Из-за этого контейнер использовал файлы с host вместо неизменяемого кода, встроенного в versioned registry image.

Даже read-only bind mount нарушает воспроизводимость image: содержимое контейнера начинает зависеть от текущего состояния host filesystem.

## Минимальное исправление

Удалить source-code bind mounts из production-like конфигурации.

Backend должен сохранить только read-only mount конфигурации:

```yaml
volumes:
  - ./config/app-config.yaml:/app/config/app-config.yaml:ro
```

Worker не должен иметь source bind mounts.

## Проверка исправления

Production-like стек запускается без broken override:

```bash
docker compose   -p final-broken-06   -f compose.yaml   -f compose.prod.yaml   up -d --force-recreate database redis backend worker --wait
```

Проверки:

```bash
docker inspect final-broken-06-backend-1   | grep -F '"Destination": "/app/app.py"'   || echo "OK: backend source mount отсутствует"

docker inspect final-broken-06-worker-1   | grep -F '"Destination": "/app/worker.py"'   || echo "OK: worker source mount отсутствует"
```

Ожидается:

```text
OK: backend source mount отсутствует
OK: worker source mount отсутствует
```

Backend и worker должны оставаться healthy.

## Почему restart или prune не является исправлением

Restart повторно создаст контейнеры с теми же bind mounts.

Prune не изменяет Compose override и может удалить полезные ресурсы.

Root cause устраняется удалением source bind mounts из production-конфигурации.
