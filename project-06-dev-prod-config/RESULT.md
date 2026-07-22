# RESULT — Project 06

## Итог

Созданы три Compose-конфигурации:

- `compose.yaml` — общая база;
- `compose.override.yaml` — локальная разработка;
- `compose.prod.yaml` — production-like запуск.

Проверены:

- автоматическое применение override-файла;
- merge нескольких Compose-файлов;
- profiles;
- env precedence;
- dev bind mounts;
- production без source-code bind mount;
- read-only config;
- разные project names;
- параллельный запуск двух окружений.

## Файлы

Созданы:

- `app/Dockerfile`;
- `app/.dockerignore`;
- `compose.yaml`;
- `compose.override.yaml`;
- `compose.prod.yaml`;
- `config/dev.env`;
- `config/prod.env`;
- `evidence/`;
- `RESULT.md`.

Изменён `.gitignore`, чтобы Git отслеживал рабочие Compose-файлы и Dockerfile.

## Базовая конфигурация

`compose.yaml` содержит общие настройки:

- app image;
- PostgreSQL;
- общий config mount;
- healthchecks;
- named volume;
- dependency через `service_healthy`.

Config подключён read-only:

```yaml
volumes:
  - ./config/app-config.yaml:/app/config/app-config.yaml:ro
```

## Dev override

`compose.override.yaml` применяется автоматически при обычной команде:

```bash
docker compose up
```

Dev-режим включает:

- build локального image;
- bind mount `app.py`;
- Flask debug server;
- `config/dev.env`;
- localhost-порт приложения;
- localhost-порт PostgreSQL;
- Adminer через profile `tools`.

Source bind mount:

```yaml
volumes:
  - ./app/app.py:/app/app.py
```

Database опубликована только на localhost:

```yaml
ports:
  - "127.0.0.1:5433:5432"
```

## Production override

Production запускается явно:

```bash
docker compose   -f compose.yaml   -f compose.prod.yaml   up -d
```

Production использует:

- заранее собранный image;
- `config/prod.env`;
- отсутствие bind mount исходного кода;
- read-only root filesystem;
- tmpfs `/tmp`;
- `no-new-privileges`;
- restart policy `unless-stopped`;
- database без опубликованного host-порта.

Проверенный hardening:

```text
readonly=true
security=["no-new-privileges:true"]
restart=unless-stopped
```

Production mounts:

```text
config/app-config.yaml -> /app/config/app-config.yaml RW=false
```

Строки `/app/app.py` в production mounts нет.

## Dev окружение

Проект `dev-a`:

```bash
docker compose -p dev-a up -d --build
```

Порты:

```text
app:      127.0.0.1:8083 -> 5000
database: 127.0.0.1:5433 -> 5432
```

Ответ `/config`:

```json
{
  "environment": "development",
  "log_level": "from-dotenv",
  "file_config": {
    "feature_flags": {
      "demo": true
    },
    "message": "base-config"
  }
}
```

## Второе dev окружение

Проект `dev-b`:

```bash
APP_PORT=8085 POSTGRES_HOST_PORT=5434 docker compose -p dev-b up -d --no-build
```

Порты:

```text
app:      127.0.0.1:8085 -> 5000
database: 127.0.0.1:5434 -> 5432
```

Оба проекта работали параллельно без конфликтов.

## Production-like окружение

Проект:

```text
prod-like
```

Приложение опубликовано на:

```text
127.0.0.1:8086
```

Ответ `/config`:

```json
{
  "environment": "production",
  "log_level": "warning",
  "file_config": {
    "feature_flags": {
      "demo": true
    },
    "message": "base-config"
  }
}
```

PostgreSQL в production не имеет host port binding.

## Profiles

Adminer описан с profile:

```yaml
profiles:
  - tools
```

Без profile запускаются только:

```text
app
database
```

Adminer запускается явно:

```bash
docker compose -p dev-a --profile tools up -d adminer
```

Проверка:

```text
HTTP/1.1 200 OK
```

После проверки Adminer удалён.

## Env precedence

Использовались:

- `.env`;
- `env_file`;
- `environment`;
- CLI `-e`.

### `.env`

Используется Compose для interpolation значений:

```text
APP_PORT
APP_IMAGE
APP_VERSION
POSTGRES_DB
```

`.env` не является автоматическим env-файлом контейнера.

### `env_file`

Dev:

```yaml
env_file:
  - ./config/dev.env
```

Production:

```yaml
env_file:
  - ./config/prod.env
```

### `environment`

В dev override:

```yaml
environment:
  LOG_LEVEL: ${LOG_LEVEL:-debug}
```

Это значение имеет приоритет над `LOG_LEVEL` из `env_file`.

Поскольку в `.env` было:

```text
LOG_LEVEL=from-dotenv
```

в контейнер попало:

```text
LOG_LEVEL=from-dotenv
```

### CLI override

Команда:

```bash
docker compose run --rm   -e LOG_LEVEL=from-cli   app   python -c "..."
```

Результат:

```text
LOG_LEVEL=from-cli
```

CLI имеет наивысший приоритет для конкретного запуска.

## Compose config

Сохранены результаты:

```text
evidence/config-dev.txt
evidence/config-dev-tools.txt
evidence/config-prod.txt
```

Они показывают итог после interpolation и merge.

Из evidence удалено значение PostgreSQL password.

## Ответы на вопросы

### 1. Почему порядок `-f` важен?

Compose объединяет файлы слева направо.

Более поздний файл переопределяет или расширяет значения предыдущих.

```bash
docker compose -f compose.yaml -f compose.prod.yaml config
```

означает: сначала база, затем production override.

### 2. Что Compose объединяет, а что заменяет?

Maps обычно объединяются по ключам.

Scalar values заменяются более поздним значением.

Некоторые списки объединяются или дополняются, включая ports и volumes, в зависимости от типа поля и merge rules.

Поэтому результат всегда нужно проверять через:

```bash
docker compose config
```

### 3. Чем `.env` отличается от `env_file`?

`.env` используется Compose CLI для подстановки `${VARIABLE}`.

`env_file` передаёт переменные внутрь контейнера.

Переменная из `.env` не обязана появиться в контейнере, пока она не используется в `environment`, `env_file` или другом соответствующем поле.

### 4. Какой приоритет у `environment`?

`environment` в Compose имеет приоритет над `env_file`.

CLI override, например `-e VARIABLE=value`, имеет более высокий приоритет для конкретного запуска.

### 5. Когда полезны profiles?

Profiles полезны для необязательных сервисов:

- Adminer;
- debug tools;
- migration jobs;
- monitoring;
- development utilities.

Они не запускаются в стандартном окружении.

### 6. Почему production не должен использовать source-code bind mount?

Bind mount:

- делает контейнер зависимым от host filesystem;
- позволяет локальным изменениям менять работающий контейнер;
- нарушает воспроизводимость;
- может обходить содержимое собранного image;
- усложняет rollback и аудит.

Production должен запускать неизменяемый собранный image.

### 7. Что даёт Compose project name?

Project name создаёт namespace для:

- контейнеров;
- сетей;
- volumes;
- labels.

Благодаря разным project names можно запускать одинаковый Compose-стек параллельно, если host-порты не конфликтуют.

## Выполненные критерии

- default запуск применяет `compose.override.yaml`;
- production запускается через два явных `-f`;
- production не содержит source-code bind mount;
- Adminer не запускается без profile;
- Adminer запускается через profile `tools`;
- config подключён read-only;
- database port опубликован только в dev и только на localhost;
- production database port не опубликован;
- проверен env precedence;
- сохранены результаты `docker compose config`;
- запущены `dev-a` и `dev-b`;
- project names исключили конфликты ресурсов;
- production hardening проверен.

## Вывод

Проект показал практическую работу с:

- Compose overrides;
- merge behavior;
- profiles;
- `.env`;
- `env_file`;
- `environment`;
- CLI precedence;
- dev bind mounts;
- immutable production images;
- project names;
- параллельными окружениями.

