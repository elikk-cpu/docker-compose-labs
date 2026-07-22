# Docker & Docker Compose Labs

![Docker](https://img.shields.io/badge/Docker-Engine-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Projects](https://img.shields.io/badge/Projects-9%2F9-success)
![Level](https://img.shields.io/badge/Level-Junior%20DevOps-informational)
![Status](https://img.shields.io/badge/Status-Completed-success)

Практический репозиторий по Docker и Docker Compose: от запуска первого
контейнера до production-like стека с PostgreSQL, Redis, worker, локальным
registry, security hardening, Prometheus и Grafana.

Все девять проектов завершены, проверены по acceptance-критериям и сохранены
отдельными Git-тегами `project-01-complete` — `project-09-complete`.

## Что демонстрирует репозиторий

- воспроизводимые Docker images и versioned tags без `latest`;
- Dockerfile, build cache, layers и `.dockerignore`;
- multi-stage builds и минимизация images;
- non-root runtime, `read_only`, `tmpfs`, `cap_drop` и `no-new-privileges`;
- Compose services, DNS, networks, profiles и override-файлы;
- named volumes, persistence, healthchecks и readiness;
- PostgreSQL, Redis, RabbitMQ и background workers;
- Compose secrets и поддержка `*_FILE`;
- authenticated local registry, push/pull и image digests;
- Docker Scout image scanning;
- Prometheus metrics и Grafana provisioning;
- системная диагностика контейнерных неисправностей.

## Проекты

| № | Проект | Практический результат | Документация |
|---:|---|---|---|
| 01 | Container runtime | `docker run`, ports, mounts, networks, logs, exit codes и copy-on-write | [README](project-01-container-runtime/README.md) · [RESULT](project-01-container-runtime/RESULT.md) |
| 02 | Dockerfile API | Контейнеризация Flask API, build cache и `.dockerignore` | [README](project-02-dockerfile-api/README.md) · [RESULT](project-02-dockerfile-api/RESULT.md) |
| 03 | Secure image | Multi-stage Go image, non-root runtime, hardening и scanning | [README](project-03-secure-image/README.md) · [RESULT](project-03-secure-image/RESULT.md) |
| 04 | Compose stack | Nginx frontend, backend, Redis, service DNS и разделение сетей | [README](project-04-compose-stack/README.md) · [RESULT](project-04-compose-stack/RESULT.md) |
| 05 | Data and healthchecks | PostgreSQL, Redis, RabbitMQ, worker, persistence и readiness | [README](project-05-data-and-healthchecks/README.md) · [RESULT](project-05-data-and-healthchecks/RESULT.md) |
| 06 | Dev/prod configuration | Compose overrides, profiles, environment precedence и parallel project names | [README](project-06-dev-prod-config/README.md) · [RESULT](project-06-dev-prod-config/RESULT.md) |
| 07 | Private registry | Basic auth, tagging, push/pull, persistence и digest verification | [README](project-07-registry/README.md) · [RESULT](project-07-registry/RESULT.md) |
| 08 | Troubleshooting | Восемь воспроизводимых неисправностей с root-cause analysis | [README](project-08-troubleshooting/README.md) · [RESULT](project-08-troubleshooting/RESULT.md) |
| 09 | Final stack | Полный production-like Docker Compose проект уровня Junior DevOps | [README](project-09-final-stack/README.md) · [RUNBOOK](project-09-final-stack/RUNBOOK.md) · [RESULT](project-09-final-stack/RESULT.md) |

## Финальный стек

```text
Browser
   |
   v
Frontend (Nginx)
   |
   v
Backend (Flask/Gunicorn) ------> PostgreSQL
   |
   v
Redis queue
   |
   v
Worker ------------------------> PostgreSQL

Monitoring profile:
Prometheus ------> Backend /metrics
Grafana ---------> Prometheus
```

### Основные свойства

- наружу публикуется только frontend;
- PostgreSQL и Redis доступны только во внутренней `data` network;
- frontend отделён от database;
- backend и worker запускаются от UID/GID `10001:10001`;
- PostgreSQL password передаётся через Compose secret;
- production-like конфигурация использует registry images без source bind mounts;
- core services используют readiness-oriented healthchecks;
- monitoring запускается только через profile `monitoring`;
- Adminer запускается только через profile `tools`.

## Быстрый запуск финального dev-стека

```bash
cd project-09-final-stack

cp .env.example .env

mkdir -p secrets
openssl rand -hex 24 > secrets/postgres_password.txt
openssl rand -hex 24 > secrets/grafana_admin_password.txt

sudo chown 0:10001 secrets/postgres_password.txt
sudo chmod 0440 secrets/postgres_password.txt
chmod 0600 secrets/grafana_admin_password.txt

docker compose config
docker compose up -d --build --wait
docker compose ps
```

Проверка API:

```bash
curl -i http://127.0.0.1:8080/api/info

curl -i   -X POST   -H "Content-Type: application/json"   -d '{"task":"portfolio-demo"}'   http://127.0.0.1:8080/api/jobs

curl -i http://127.0.0.1:8080/api/jobs
```

Остановка с сохранением named volumes:

```bash
docker compose down
```

Подробные инструкции:  
[Project 09 Runbook](project-09-final-stack/RUNBOOK.md)

## Troubleshooting

В проектах 08 и 09 воспроизведены и диагностированы типовые проблемы:

- container exits with code `0`, но сервис не работает;
- опубликован неправильный container port;
- `localhost` используется вместо Compose service name;
- non-root процесс не имеет прав записи;
- container `running`, но `unhealthy`;
- фиксированный `container_name` создаёт конфликт;
- PostgreSQL init SQL не применяется к существующему volume;
- registry authentication и отсутствующий tag;
- backend не получает secret;
- production override возвращает source bind mounts;
- worker запускается от root.

Для каждого сценария сохранены symptom, evidence, root cause, минимальное
исправление и проверка результата.

## Структура репозитория

```text
docker-compose-labs/
├── project-01-container-runtime/
├── project-02-dockerfile-api/
├── project-03-secure-image/
├── project-04-compose-stack/
├── project-05-data-and-healthchecks/
├── project-06-dev-prod-config/
├── project-07-registry/
├── project-08-troubleshooting/
├── project-09-final-stack/
├── docs/
├── scripts/
└── VERSIONS.md
```

## Принципы выполнения

- не использовать `latest`;
- не коммитить реальные secrets и локальные `.env`;
- не использовать `--privileged` без обоснования;
- проверять итоговый merge через `docker compose config`;
- не использовать restart или prune вместо root-cause analysis;
- публиковать наружу только необходимые ports;
- изменять инфраструктуру декларативно, а не вручную внутри контейнера;
- фиксировать acceptance evidence и инженерные решения в `RESULT.md`.

## Git history

Каждый проект выполнялся в отдельной ветке, после приёмки объединялся с
`main` и отмечался тегом:

```text
project-01-complete
project-02-complete
project-03-complete
project-04-complete
project-05-complete
project-06-complete
project-07-complete
project-08-complete
project-09-complete
```

## Следующий этап

Следующее развитие репозитория:

- GitHub Actions CI;
- автоматическая проверка Compose;
- build и smoke tests;
- image vulnerability scanning;
- публикация versioned images;
- дальнейшая миграция финального стека в Kubernetes и Helm.

