# RESULT — Project 02

## Краткий итог

Я контейнеризировал Flask API и собрал image `lab-api:0.1.0`.

Приложение запускается через Gunicorn, слушает `0.0.0.0:5000` внутри контейнера и доступно на `127.0.0.1:5000` виртуальной машины.

## Что я создал или изменил

- Создал `Dockerfile`.
- Создал `.dockerignore`.
- Изменил `.gitignore`, чтобы Git отслеживал `Dockerfile` и `.dockerignore`.
- Создал каталог `evidence/`.
- Подготовил `RESULT.md`.

## Архитектура и принятые решения

Схема:

`127.0.0.1:5000` хоста → `0.0.0.0:5000` контейнера → Gunicorn → Flask API.

Порядок слоёв Dockerfile:

1. `FROM` — versioned Python image.
2. `ARG APP_VERSION`.
3. `ENV` — runtime-переменные.
4. `WORKDIR /app`.
5. `COPY requirements.txt .`.
6. `RUN pip install`.
7. `COPY app/ .`.
8. `EXPOSE 5000`.
9. `CMD` — Gunicorn в exec-форме.

Такой порядок позволяет не переустанавливать зависимости при изменении только `app.py`.

## Dockerfile

```dockerfile
FROM python:3.13.14-slim-bookworm

ARG APP_VERSION=dev

ENV APP_VERSION=${APP_VERSION} \
    APP_HOST=0.0.0.0 \
    APP_PORT=5000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## .dockerignore

```text
.git
.gitignore
.env
.env.local
.venv/
__pycache__/
*.pyc
*.pyo
*.log
README.md
acceptance.md
questions.md
RESULT.md
RESULT_TEMPLATE.md
evidence/
notes/
Dockerfile.todo
.dockerignore.todo
```

## Команды сборки и запуска

Сборка:

```bash
docker build \
  --build-arg APP_VERSION=0.1.0 \
  -t lab-api:0.1.0 \
  .
```

Запуск:

```bash
docker run -d \
  --name lab-api \
  -p 127.0.0.1:5000:5000 \
  lab-api:0.1.0
```

Удаление:

```bash
docker rm -f lab-api
```

## Проверки из acceptance.md

Проверка image:

```bash
docker image ls lab-api
```

Проверка контейнера:

```bash
docker ps --filter name=lab-api
```

Проверка `/healthz`:

```bash
curl -i http://localhost:5000/healthz
```

Результат:

```text
HTTP/1.1 200 OK
{"status":"ok"}
```

Проверка `/api/info`:

```bash
curl -i http://localhost:5000/api/info
```

Результат содержит:

```text
"host":"0.0.0.0"
"port":"5000"
"service":"dockerfile-api"
"version":"0.1.0"
```

Проверка версии Python:

```bash
docker run --rm lab-api:0.1.0 python --version
```

Проверка конфигурации image:

```bash
docker image inspect lab-api:0.1.0 \
  --format 'cmd={{json .Config.Cmd}} env={{json .Config.Env}}'
```

Проверка слоёв:

```bash
docker history lab-api:0.1.0
```

## Проверка build cache

После изменения только `app/app.py`:

- `WORKDIR /app` — `CACHED`;
- `COPY requirements.txt .` — `CACHED`;
- `RUN pip install ...` — `CACHED`;
- `COPY app/ .` — выполнен заново.

Причина: `requirements.txt` не изменился, поэтому слой установки зависимостей остался валидным.

## Ошибки и root cause

### Поломка 1. Приложение слушает 127.0.0.1

Контейнер был запущен с `APP_HOST=127.0.0.1`.

Логи показали:

```text
Running on http://127.0.0.1:5000
```

Контейнер был `running`, но запрос через опубликованный порт завершался ошибкой.

Root cause: `127.0.0.1` внутри контейнера — loopback самого контейнера. Для доступа через port publishing приложение должно слушать `0.0.0.0`.

### Поломка 2. Неверный основной процесс

Я заменил основной процесс на:

```bash
echo "wrong process"
```

Команда завершилась сразу, поэтому контейнер перешёл в `Exited`.

Root cause: контейнер существует, пока работает его PID 1.

## Best practices

- Использован конкретный base image tag.
- Создан `.dockerignore`.
- Исключены `.git`, `.env`, virtualenv, bytecode и logs.
- Зависимости копируются и устанавливаются до кода приложения.
- Использован `pip --no-cache-dir`.
- Использован Gunicorn.
- Использована exec-форма `CMD`.
- Приложение слушает `0.0.0.0`.
- Порт опубликован только на localhost хоста.
- Версия приложения передана через `ARG` и сохранена в `ENV`.
- Контейнер не изменялся вручную через `docker exec`.

## Что осталось улучшить

В проекте 03:

- multi-stage build;
- non-root user;
- уменьшение размера;
- read-only filesystem;
- `cap_drop`;
- `no-new-privileges`;
- image scanning.

## Ответы на диагностические вопросы

### Чем ARG отличается от ENV?

`ARG` доступен во время сборки. `ENV` сохраняется в image и доступен контейнеру во время запуска.

### Что такое build context?

Набор файлов, доступных команде `docker build`.

### Почему нужен .dockerignore?

Он уменьшает build context и предотвращает попадание лишних или чувствительных файлов в image.

### Почему приложение должно слушать 0.0.0.0?

Чтобы принимать соединения через сетевой интерфейс контейнера, а не только через loopback.

### Чем CMD отличается от ENTRYPOINT?

`ENTRYPOINT` задаёт основной executable. `CMD` задаёт команду по умолчанию или аргументы.

### Почему exec-форма лучше shell-формы?

Процесс запускается напрямую как PID 1 и корректнее получает сигналы завершения.

### Что влияет на invalidation cache?

Изменение инструкции Dockerfile, её аргументов или файлов, используемых `COPY`/`ADD`.

### Что такое image layers?

Неизменяемые слои, создаваемые инструкциями Dockerfile.

