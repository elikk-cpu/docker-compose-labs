# Broken scenario 01 — Backend uses localhost instead of database

## Symptom

Backend запустился, но стал `unhealthy`.

Frontend не стартовал, потому что ожидал:

```yaml
depends_on:
  backend:
    condition: service_healthy
```

Backend endpoint `/readyz` возвращал:

```text
HTTP 503
```

## Команды диагностики

```bash
docker compose   -p final-broken-01   -f compose.yaml   -f compose.prod.yaml   -f broken/case-01/compose.broken.yaml   ps -a

docker inspect <backend-container>

docker exec <backend-container>   python -c "import socket; print(socket.gethostbyname('database'))"
```

## Evidence

Переменная backend:

```text
POSTGRES_HOST=localhost
```

Ответ `/readyz`:

```text
status: 503
```

Ошибка подключения:

```text
connection to server at "127.0.0.1", port 5432 failed:
Connection refused
```

Docker DNS при этом работал:

```text
database=172.22.0.3
```

## Root cause

Внутри backend-контейнера `localhost` указывает на сам backend-контейнер.

PostgreSQL работает в отдельном контейнере, поэтому backend должен подключаться к service name:

```text
database
```

через внутренний Docker DNS.

## Минимальное исправление

Было:

```yaml
services:
  backend:
    environment:
      POSTGRES_HOST: localhost
```

Стало:

```yaml
services:
  backend:
    environment:
      POSTGRES_HOST: database
```

## Проверка исправления

```bash
FRONTEND_PORT=8181 docker compose   -p final-broken-01   -f compose.yaml   -f compose.prod.yaml   -f broken/case-01/compose.fixed.yaml   up -d --wait
```

Backend readiness:

```text
{"status":"ready"}
```

## Дополнительное наблюдение

При первой попытке port `8181` был добавлен в override как новый элемент списка `ports`.

Compose объединил ports базового и override-файла, поэтому сохранился также host port `8080`, уже занятый production-стеком.

Для изоляции broken-окружения host port был передан через interpolation:

```bash
FRONTEND_PORT=8181 docker compose ...
```

## Почему restart или prune не является исправлением

Restart повторно запустил бы backend с:

```text
POSTGRES_HOST=localhost
```

и `/readyz` снова вернул бы `503`.

Prune не исправил бы значение environment.

Root cause устраняется заменой `localhost` на Docker service name `database`.
