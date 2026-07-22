# RESULT — Project 09 Final Docker Stack

## Итог

Собран и проверен production-like Docker Compose stack уровня Junior DevOps.

Архитектура:

```text
Browser -> frontend -> backend -> PostgreSQL
                         |
                         +-> Redis queue -> worker -> PostgreSQL

Prometheus -> backend /metrics
Grafana -> Prometheus
```

## Реализовано

### Images и Dockerfiles

Созданы три собственных Dockerfile:

```text
frontend/Dockerfile
backend/Dockerfile
worker/Dockerfile
```

Backend и worker используют multi-stage builds и запускаются от:

```text
10001:10001
```

Для всех build contexts созданы `.dockerignore`.

### Compose

Созданы:

```text
compose.yaml
compose.override.yaml
compose.prod.yaml
```

Dev использует build и bind mounts для разработки.

Production-like использует versioned registry images и не монтирует исходный код.

### Networks

Использованы отдельные networks:

```text
edge
data
monitoring
```

Frontend не подключён к data network.

Database и Redis не подключены к edge network.

### Persistence

Использованы named volumes:

```text
postgres_data
redis_data
prometheus_data
grafana_data
```

PostgreSQL data пережили удаление и пересоздание database-контейнера.

### Secrets

PostgreSQL password передаётся как Compose secret:

```text
/run/secrets/postgres_password
```

Backend и worker поддерживают:

```text
POSTGRES_PASSWORD_FILE
```

Secret не встроен в image и не хранится в committed `.env`.

### Healthchecks и readiness

Healthy dependencies используются через:

```yaml
condition: service_healthy
```

Проверяются реальные capabilities:

- PostgreSQL принимает соединения;
- Redis отвечает `PONG`;
- backend `/readyz` подключается к PostgreSQL и Redis;
- worker healthcheck подключается к PostgreSQL и Redis;
- frontend обслуживает HTTP.

Core stack становится healthy.

### Job flow

Проверен полный путь:

```text
frontend
-> backend
-> Redis queue
-> worker
-> PostgreSQL
```

Задача появилась в таблице:

```text
processed_jobs
```

### Production-like ограничения

Подтверждено:

- PostgreSQL не опубликован наружу;
- Redis не опубликован наружу;
- наружу опубликован frontend;
- source bind mounts отсутствуют;
- backend и worker non-root;
- read-only FS, tmpfs, cap drop и no-new-privileges применены.

### Profiles

`tools`:

```text
Adminer
```

`monitoring`:

```text
Prometheus
Grafana
```

Monitoring не запускается без profile.

### Monitoring

Prometheus получает backend metrics с:

```text
backend:8000/metrics
```

Query:

```text
up{job="backend"}
```

возвращает:

```text
1
```

Grafana отвечает `HTTP 200`.

Datasource `Prometheus` provisioned автоматически:

```text
url=http://prometheus:9090
isDefault=true
```

### Registry

Опубликованы versioned images:

```text
localhost:5000/labuser/final-frontend:1.0.0
localhost:5000/labuser/final-backend:1.0.0
localhost:5000/labuser/final-worker:1.0.0
```

Проверен workflow:

```text
tag -> push -> remove local image -> pull
```

Digest после pull совпадает с digest опубликованного image.

`latest` не использовался.

### Image scanning

Docker Scout reports сохранены в:

```text
evidence/scans/
```

Scan summary:

```text
final-frontend: 0 Critical, 0 High
final-backend: 1 Critical, 2 High
final-worker: 1 Critical, 2 High
```

Critical/High findings относятся к пакетам базового Debian image и на момент scan были отмечены как not fixed.

Для Flask была обнаружена доступная более новая исправленная версия.

Опубликованный tag `1.0.0` не перезаписывается. Security fixes должны публиковаться новым version tag.

## Broken scenarios

Воспроизведены, диагностированы и исправлены восемь сценариев:

1. Backend использует `localhost` вместо service name `database`.
2. Nginx proxy использует неправильный backend port.
3. PostgreSQL init changes не применяются к существующему volume.
4. Healthcheck проверяет несуществующий endpoint.
5. Backend не получает PostgreSQL secret.
6. Production override возвращает source-code bind mounts.
7. Worker запускается от root.
8. Registry tag отсутствует.

Для каждого кейса сохранены:

- symptom;
- evidence;
- root cause;
- минимальное исправление;
- проверка исправления;
- объяснение, почему restart/prune не является анализом.

Документы:

```text
diagnosis/final-case-01.md
diagnosis/final-case-02.md
diagnosis/final-case-03.md
diagnosis/final-case-04.md
diagnosis/final-case-05.md
diagnosis/final-case-06.md
diagnosis/final-case-07.md
diagnosis/final-case-08.md
```

## Acceptance

Выполнено:

- все Compose-файлы проходят `docker compose config`;
- core stack healthy;
- frontend выполняет API requests;
- job проходит очередь и появляется в PostgreSQL;
- PostgreSQL persistence доказана;
- secret доступен нужным сервисам;
- backend/worker non-root;
- database/Redis не опубликованы наружу в production-like config;
- monitoring работает только через profile;
- Grafana datasource provisioned;
- images имеют versioned registry tags;
- scan reports приложены;
- broken scenarios документированы.

## Основные выводы

- Container `running` не означает service `ready`.
- Compose service names используются как внутренние DNS names.
- `localhost` внутри контейнера указывает на этот же контейнер.
- Named volume и migrations решают разные задачи.
- Secret должен быть явно выдан каждому сервису.
- Runtime Compose settings могут переопределить Dockerfile `USER`.
- Production image должен быть воспроизводимым и не зависеть от source bind mounts.
- Tag изменяем, digest идентифицирует конкретное содержимое.
- Restart и prune не заменяют диагностику root cause.

## Статус

```text
PROJECT 09: COMPLETE
DOCKER / DOCKER COMPOSE PRACTICAL BLOCK: COMPLETE
```

