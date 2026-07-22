# Broken scenario 05 — PostgreSQL secret is not granted to backend

## Symptom

Backend запускался, но становился:

```text
unhealthy
```

Frontend не мог стартовать из-за зависимости:

```yaml
depends_on:
  backend:
    condition: service_healthy
```

## Broken configuration

Из backend был полностью удалён Compose secret:

```yaml
services:
  backend:
    secrets: !override []
```

Итоговая Compose-конфигурация не выдавала backend файл:

```text
/run/secrets/postgres_password
```

## Root cause

Backend использует переменную:

```text
POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
```

Функция `read_secret()` пытается прочитать этот файл для подключения к PostgreSQL.

Когда secret не выдан сервису, файл отсутствует. Readiness-проверка не может подключиться к базе, и backend становится `unhealthy`.

## Минимальное исправление

Было:

```yaml
services:
  backend:
    secrets: !override []
```

Стало:

```yaml
services:
  backend:
    secrets:
      - postgres_password
```

## Проверка исправления

```bash
FRONTEND_PORT=8185 docker compose   -p final-broken-05   -f compose.yaml   -f compose.prod.yaml   -f broken/case-05/compose.fixed.yaml   up -d database redis backend --wait
```

После исправления:

```text
database healthy
redis healthy
backend healthy
```

Backend healthcheck обращается к `/readyz`. Этот endpoint читает PostgreSQL secret и выполняет реальное подключение к database.

Следовательно, состояние `backend healthy` подтверждает одновременно:

- secret выдан backend;
- файл доступен процессу;
- пароль прочитан;
- PostgreSQL connection успешно установлен.

## Почему restart или prune не является исправлением

Restart снова запускал бы backend без secret.

Файл `/run/secrets/postgres_password` не появился бы, и backend снова стал бы `unhealthy`.

Prune не изменяет Compose grants.

Root cause устраняется выдачей `postgres_password` нужному сервису.
