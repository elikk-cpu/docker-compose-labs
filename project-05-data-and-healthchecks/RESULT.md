# RESULT — Project 05

## Итог

Собран стек:

```text
API -> PostgreSQL
API -> Redis
API -> RabbitMQ -> Worker -> PostgreSQL
```

Сервисы:
- `api` — Flask API под Gunicorn;
- `database` — PostgreSQL;
- `redis` — счётчик отправленных задач;
- `rabbitmq` — очередь;
- `worker` — обработчик задач.

Все зависимости имеют healthchecks. API и worker используют `condition: service_healthy`.

## Named volumes

```yaml
volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
```

- `postgres_data` хранит таблицы и обработанные задачи.
- `redis_data` хранит счётчик submitted.
- `rabbitmq_data` хранит состояние RabbitMQ.

## PostgreSQL

Image:

```text
postgres:17.10-alpine3.23
```

Таблица:

```sql
CREATE TABLE IF NOT EXISTS processed_jobs (
    id BIGSERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Healthcheck:

```yaml
test:
  - CMD-SHELL
  - pg_isready -U "$${POSTGRES_USER}" -d "$${POSTGRES_DB}"
```

## Redis

Image:

```text
redis:8.6.4-alpine3.23
```

Включён AOF:

```yaml
command:
  - redis-server
  - --appendonly
  - "yes"
```

Healthcheck:

```yaml
test:
  - CMD
  - redis-cli
  - ping
```

## RabbitMQ

Image:

```text
rabbitmq:4.3.1-management-alpine
```

Используется отдельный пользователь:

```text
labuser
```

Healthcheck проверяет:

```bash
rabbitmq-diagnostics -q ping
rabbitmqctl authenticate_user "$RABBITMQ_DEFAULT_USER" "$RABBITMQ_DEFAULT_PASS"
```

Пользователь `guest` не используется.

## API

Endpoints:

```text
GET  /healthz
GET  /readyz
POST /jobs
GET  /stats
```

`/healthz` проверяет liveness процесса.

`/readyz` проверяет реальные зависимости:

- PostgreSQL через `SELECT 1`;
- Redis через `PING`;
- RabbitMQ через AMQP connection.

При готовом стеке:

```text
HTTP 200
```

```json
{"checks":{"postgres":"ok","rabbitmq":"ok","redis":"ok"}}
```

`POST /jobs` публикует persistent message в durable queue `jobs` и увеличивает `jobs_submitted` в Redis.

Проверка:

```bash
curl -i   -X POST   -H "Content-Type: application/json"   -d '{"task":"final-project-05-test"}'   http://localhost:8082/jobs
```

Результат:

```text
HTTP/1.1 202 ACCEPTED
```

## Worker

Worker читает queue `jobs` и записывает payload в PostgreSQL.

В логах:

```text
processed: {'task': 'final-project-05-test'}
```

В таблице появилась строка:

```text
{"task": "final-project-05-test"}
```

## Persistence

В PostgreSQL была добавлена запись:

```json
{"task":"persistence-test"}
```

После:

```bash
docker compose stop database
docker compose rm -f database
docker compose up -d database
```

запись сохранилась.

Причина: данные находились в named volume, а не в writable layer контейнера.

## `down` и `down -v`

`docker compose down` удаляет контейнеры и сети, но сохраняет named volumes.

После обычного `down` данные PostgreSQL сохранились.

`docker compose down -v` удаляет также named volumes проекта.

После повторного запуска:

```json
{"processed":0,"submitted":0}
```

## Running, но not ready

Был остановлен RabbitMQ:

```bash
docker compose stop rabbitmq
```

При этом:

```text
GET /healthz -> HTTP 200
GET /readyz  -> HTTP 503
```

Контейнер API оставался running, но health status стал:

```text
unhealthy
```

После запуска RabbitMQ:

```bash
docker compose start rabbitmq
```

API восстановился:

```text
GET /readyz -> HTTP 200
```

и снова стал healthy.

## Повторные подключения worker

Во время недоступности RabbitMQ worker писал:

```text
rabbitmq not ready: Temporary failure in name resolution
```

После восстановления RabbitMQ:

```text
worker waiting for jobs
```

Затем worker успешно обработал новую задачу.

## Сеть сборки

Bridge-контейнеры VM не имели исходящего доступа к PyPI.

Для установки Python-зависимостей использовано:

```yaml
build:
  network: host
```

Это действует только во время build. Runtime-сервисы остаются в изолированной Compose-сети.

## Выполненные критерии

- `docker compose config` проходит;
- PostgreSQL healthy;
- Redis healthy;
- RabbitMQ healthy;
- API healthy;
- `/readyz` возвращает 200;
- `POST /jobs` создаёт задачу;
- worker обрабатывает задачу;
- worker пишет результат в PostgreSQL;
- `/stats` показывает submitted и processed;
- данные переживают пересоздание database container;
- RabbitMQ использует `labuser`;
- database, Redis и RabbitMQ не опубликованы на host;
- проверены `down` и `down -v`;
- воспроизведён running, но not ready.

## Ответы на вопросы

### 1. Почему `depends_on` без condition недостаточен?

Он гарантирует порядок запуска контейнеров, но не готовность приложений внутри них.

`condition: service_healthy` ожидает успешный healthcheck.

### 2. Что делает хороший healthcheck?

Проверяет реальную capability сервиса: подключение к БД, Redis PING, AMQP authentication или доступность зависимостей API.

### 3. Чем liveness отличается от readiness?

Liveness отвечает, жив ли процесс.

Readiness отвечает, готов ли сервис выполнять полноценные запросы.

### 4. Почему `guest/guest` не подходит для RabbitMQ между контейнерами?

`guest` предназначен для локального доступа. Для сервисного взаимодействия нужен отдельный пользователь с отдельным паролем и контролируемыми правами.

### 5. Что сохраняется после `down`, а что после `down -v`?

После `down` named volumes сохраняются.

После `down -v` named volumes проекта удаляются.

### 6. Почему named volume предпочтительнее bind mount для PostgreSQL?

Named volume управляется Docker, меньше зависит от путей и прав host filesystem и лучше подходит для внутренних данных СУБД.

### 7. Почему healthcheck не должен проверять только наличие процесса?

Процесс может существовать, но не принимать подключения, не завершить инициализацию или иметь недоступные зависимости.

## Вывод

Проект отработал:

- persistence;
- named volumes;
- healthchecks;
- liveness/readiness;
- `service_healthy`;
- RabbitMQ producer/consumer;
- worker;
- PostgreSQL initialization;
- Redis counters;
- recovery;
- последствия `down -v`.

