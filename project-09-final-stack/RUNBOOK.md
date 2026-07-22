# RUNBOOK — Project 09 Final Docker Stack

## Архитектура

```text
Browser
  |
  v
frontend (Nginx)
  |
  v
backend (Flask/Gunicorn)
  |                  |
  v                  v
PostgreSQL       Redis queue
                     |
                     v
                   worker
                     |
                     v
                 PostgreSQL

Monitoring profile:
Prometheus -> backend:/metrics
Grafana -> Prometheus
```

## Сервисы

- `frontend` — статический frontend и reverse proxy к backend.
- `backend` — API, readiness и Prometheus metrics.
- `worker` — получает jobs из Redis и записывает результаты в PostgreSQL.
- `database` — PostgreSQL с named volume.
- `redis` — очередь задач с named volume.
- `adminer` — profile `tools`.
- `prometheus` и `grafana` — profile `monitoring`.

## Используемые images

```text
nginx:1.30.4-alpine3.24
python:3.13.14-slim-bookworm
postgres:17.10-alpine3.23
redis:8.6.4-alpine3.23
prom/prometheus:v3.4.0
grafana/grafana:12.2.10-ubuntu
```

Собственные versioned images:

```text
localhost:5000/labuser/final-frontend:1.0.0
localhost:5000/labuser/final-backend:1.0.0
localhost:5000/labuser/final-worker:1.0.0
```

## Подготовка

Создать локальный `.env`:

```bash
cp .env.example .env
```

Создать secrets:

```bash
mkdir -p secrets
openssl rand -hex 24 > secrets/postgres_password.txt
openssl rand -hex 24 > secrets/grafana_admin_password.txt
chmod 600 secrets/*.txt
```

PostgreSQL secret должен быть доступен non-root backend и worker:

```bash
sudo chown 0:10001 secrets/postgres_password.txt
sudo chmod 0440 secrets/postgres_password.txt
```

Secrets и `.env` не коммитятся.

## Dev-запуск

```bash
docker compose config
docker compose up -d --build --wait
docker compose ps
```

Frontend:

```text
http://127.0.0.1:8080
```

PostgreSQL в dev:

```text
127.0.0.1:5436
```

Проверка API:

```bash
curl -i http://127.0.0.1:8080/api/info
curl -i -X POST   -H "Content-Type: application/json"   -d '{"task":"runbook"}'   http://127.0.0.1:8080/api/jobs
curl -i http://127.0.0.1:8080/api/jobs
```

## Tools profile

```bash
docker compose --profile tools up -d adminer
docker compose --profile tools ps
```

Adminer:

```text
http://127.0.0.1:8089
```

Остановка:

```bash
docker compose --profile tools rm -sf adminer
```

## Production-like запуск

Локальный registry должен быть запущен, а versioned images опубликованы.

```bash
docker compose   -p final-prod   -f compose.yaml   -f compose.prod.yaml   config
```

```bash
docker compose   -p final-prod   -f compose.yaml   -f compose.prod.yaml   up -d --pull always --wait
```

Проверка:

```bash
docker compose   -p final-prod   -f compose.yaml   -f compose.prod.yaml   ps
```

В production-like конфигурации наружу публикуется только frontend.

PostgreSQL и Redis не имеют host port bindings.

## Monitoring profile

```bash
docker compose   -p final-prod   -f compose.yaml   -f compose.prod.yaml   --profile monitoring   up -d
```

Prometheus:

```text
http://127.0.0.1:9090
```

Grafana:

```text
http://127.0.0.1:3000
```

Проверки:

```bash
curl -i http://127.0.0.1:9090/-/ready
curl -i http://127.0.0.1:3000/api/health
```

Prometheus target:

```bash
curl -sS   'http://127.0.0.1:9090/api/v1/query?query=up%7Bjob%3D%22backend%22%7D'
```

Ожидаемое значение:

```text
1
```

Grafana datasource provisioned автоматически:

```text
name: Prometheus
url: http://prometheus:9090
isDefault: true
```

## Persistence PostgreSQL

Удаление database-контейнера без удаления volume:

```bash
docker compose stop database
docker compose rm -f database
docker compose up -d database
docker compose up -d --wait
```

Данные в `processed_jobs` должны сохраниться.

`docker compose down` сохраняет named volumes.

`docker compose down -v` удаляет named volumes и данные.

## Security checks

Backend и worker:

```bash
docker compose exec backend id
docker compose exec worker id
```

Ожидается:

```text
uid=10001(app) gid=10001(app)
```

Hardening:

- `read_only: true`;
- `tmpfs: /tmp`;
- `cap_drop: ALL`;
- `no-new-privileges:true`;
- non-root runtime;
- отдельные `edge`, `data` и `monitoring` networks;
- наружу публикуются только необходимые ports.

## Registry workflow

```bash
docker login localhost:5000
docker tag final-backend:1.0.0   localhost:5000/labuser/final-backend:1.0.0
docker push localhost:5000/labuser/final-backend:1.0.0
docker pull localhost:5000/labuser/final-backend:1.0.0
```

Не использовать `latest`.

Digest фиксирует неизменяемое содержимое image.

## Image scanning

```bash
docker scout cves   local://localhost:5000/labuser/final-backend:1.0.0
```

Scan reports находятся в:

```text
evidence/scans/
```

Найденные vulnerabilities рассматриваются как security backlog.

Version tag `1.0.0` не перезаписывается. Исправления публикуются новым version tag.

## Диагностика

Основные команды:

```bash
docker compose ps -a
docker compose logs --tail=100
docker compose config
docker inspect <container>
docker network inspect <network>
docker volume inspect <volume>
docker image inspect <image>
```

### DNS failure

```text
Temporary failure in name resolution
```

Проверить service name и networks.

### Connection refused

Имя/IP доступен, но процесс не слушает указанный port.

Проверить реальный internal port.

### Timeout

Проверить routing, firewall, зависший сервис и network connectivity.

### Running, но unhealthy

Проверить:

```bash
docker inspect <container>
```

и `.State.Health.Log`.

### PostgreSQL init не применяется повторно

`/docker-entrypoint-initdb.d` выполняется только на пустом data directory.

Для существующей базы применять migrations.

### Registry pull error

- `unauthorized` — authentication/authorization;
- `not found` или `manifest unknown` — repository/tag отсутствует.

## Broken scenarios

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

Разобраны:

1. Backend использует `localhost`.
2. Неверный target port frontend proxy.
3. PostgreSQL volume сохраняет старые данные.
4. Healthcheck проверяет неверный endpoint.
5. Secret не выдан backend.
6. Production возвращает source bind mounts.
7. Worker запускается от root.
8. Registry tag отсутствует.

## Остановка

Dev:

```bash
docker compose down
```

Production-like и monitoring:

```bash
docker compose   -p final-prod   -f compose.yaml   -f compose.prod.yaml   --profile monitoring   down
```

Для сохранения данных не добавлять `-v`.

## Полная очистка учебного окружения

Только когда данные больше не нужны:

```bash
docker compose down -v --remove-orphans
```

Не использовать `docker system prune -a` как универсальное исправление.

