# RESULT — Project 03

## Краткий итог

Я преобразовал небезопасный Go image в компактный production-oriented image.

Итоговый image: secure-go-api:0.1.1

Результат:
- multi-stage build;
- final image на базе scratch;
- Go toolchain отсутствует в runtime image;
- процесс запускается от UID/GID 10001:10001;
- root filesystem работает в read-only режиме;
- удалены Linux capabilities;
- включён no-new-privileges;
- размер image уменьшен примерно с 519 MB до 8 MB disk usage;
- после обновления Go до 1.25.12 Docker Scout не обнаружил уязвимостей.

## Что я создал или изменил

Создано:
- Dockerfile;
- .dockerignore;
- evidence/;
- RESULT.md.

Изменено:
- .gitignore — разрешено отслеживание Dockerfile и .dockerignore;
- VERSIONS.md — Go builder обновлён с 1.24.13 до 1.25.12 после CVE-сканирования.

## Исходная проблема

Исходный Dockerfile:

```dockerfile
FROM golang:1.24.13-alpine3.23
WORKDIR /app
COPY . .
RUN go build -o server ./cmd/api
CMD ["./server"]
```

Проблемы:
- compiler и build tools оставались в final image;
- процесс запускался от root;
- COPY . . копировал лишние файлы;
- secrets могли попасть в image;
- image был большим;
- отсутствовал runtime hardening;
- бинарник был собран уязвимой Go stdlib.

## Итоговый Dockerfile

```dockerfile
FROM golang:1.25.12-alpine3.23 AS builder

WORKDIR /src

COPY go.mod ./
RUN go mod download

COPY cmd/ ./cmd/

RUN CGO_ENABLED=0 GOOS=linux \
    go build \
    -trimpath \
    -ldflags="-s -w" \
    -o /out/server \
    ./cmd/api

FROM scratch

ARG APP_VERSION=dev

ENV APP_VERSION=${APP_VERSION} \
    APP_PORT=8080

COPY --from=builder /out/server /server

USER 10001:10001

EXPOSE 8080

ENTRYPOINT ["/server"]
```

## .dockerignore

```text
.git
.gitignore
.env
.env.local
secrets/
notes/
evidence/
RESULT.md
RESULT_TEMPLATE.md
README.md
acceptance.md
questions.md
Dockerfile.insecure
Dockerfile.todo
*.log
```

## Команды сборки

Небезопасный image:

```bash
docker build -f Dockerfile.insecure -t secure-go-api:insecure .
```

Первая безопасная версия:

```bash
docker build \
  --build-arg APP_VERSION=0.1.0 \
  -t secure-go-api:0.1.0 \
  .
```

Исправленная версия после обновления Go:

```bash
docker build \
  --build-arg APP_VERSION=0.1.1 \
  -t secure-go-api:0.1.1 \
  .
```

## Команда запуска с hardening

```bash
docker run -d \
  --name secure-go-api \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  --security-opt no-new-privileges=true \
  -p 127.0.0.1:8080:8080 \
  secure-go-api:0.1.1
```

## Проверки

Пользователь image:

```bash
docker image inspect secure-go-api:0.1.1 \
  --format 'user={{.Config.User}}'
```

Ожидаемый результат:

```text
user=10001:10001
```

Процесс:

```bash
docker top secure-go-api -eo user,pid,comm
```

API:

```bash
curl -i http://localhost:8080/healthz
curl -i http://localhost:8080/api/info
```

Отсутствие Go toolchain:

```bash
docker run --rm \
  --entrypoint go \
  secure-go-api:0.1.1 \
  version
```

Ожидаемая ошибка:

```text
executable file not found
```

Hardening:

```bash
docker inspect secure-go-api \
  --format 'readonly={{.HostConfig.ReadonlyRootfs}} capdrop={{json .HostConfig.CapDrop}} security={{json .HostConfig.SecurityOpt}}'
```

Ожидаемые значения:
- readonly=true;
- capdrop=["ALL"];
- security=["no-new-privileges"].

## Сравнение размеров

Команда:

```bash
docker image ls secure-go-api
```

Результат:
- insecure image — примерно 519 MB;
- secure image — примерно 8.13 MB disk usage;
- Scout показал content size около 2.5 MB.

Безопасный image стал примерно в 60+ раз меньше.

## Docker Scout и CVE

Первая версия на Go 1.24.13:

```bash
docker scout cves local://secure-go-api:0.1.0
```

Результат:
- 0 Critical;
- 10 High;
- 9 Medium;
- 1 Low;
- 2 Unspecified;
- всего 22 уязвимости.

Уязвимости находились в Go stdlib, встроенной в статический бинарник.

После обновления builder до Go 1.25.12 и пересборки:

```bash
docker scout cves local://secure-go-api:0.1.1
```

Результат:

```text
No vulnerable packages detected
0 Critical
0 High
0 Medium
0 Low
```

## Ошибки и root cause

### Слишком большой image

Root cause: builder и runtime находились в одном stage.

Исправление: multi-stage build и scratch runtime.

### Запуск от root

Root cause: отсутствовала инструкция USER.

Исправление:

```dockerfile
USER 10001:10001
```

### Лишние и чувствительные файлы

Root cause: COPY . . без корректного .dockerignore.

Исправление:
- создан .dockerignore;
- копируются только go.mod и cmd/;
- secrets исключены.

### CVE в минимальном image

Root cause: статический бинарник был собран уязвимой Go stdlib 1.24.13.

Scratch удалил ОС-пакеты, но не уязвимости внутри бинарника.

Исправление: обновление Go до 1.25.12 и повторная сборка.

## Best practices

- Multi-stage build.
- Отдельный builder и runtime.
- Scratch runtime.
- Конкретный versioned base image.
- Non-root UID/GID.
- .dockerignore.
- Secrets исключены из build context.
- CGO_ENABLED=0.
- -trimpath.
- -ldflags="-s -w".
- Exec-форма ENTRYPOINT.
- Read-only root filesystem.
- tmpfs для временной записи.
- cap-drop=ALL.
- no-new-privileges.
- Порт опубликован только на localhost.
- CVE scanning.
- Повторное сканирование после исправления.

## Что осталось улучшить

В реальном production:
- pin image по digest;
- генерировать SBOM;
- подписывать image;
- запускать scanning в CI;
- добавить healthcheck;
- добавить resource limits;
- регулярно пересобирать image.

## Ответы на диагностические вопросы

### Почему multi-stage уменьшает attack surface?

Build tools остаются в builder stage и не попадают в runtime image.

### Что non-root защищает, а что не защищает?

Non-root снижает последствия компрометации процесса, но не исправляет уязвимости приложения и конфигурации.

### Зачем cap-drop=ALL?

Удаляет Linux capabilities, которые приложению не нужны.

### Что делает no-new-privileges?

Запрещает процессу получать дополнительные привилегии.

### Почему secret нельзя передавать через ARG?

ARG может попасть в metadata, history, logs или cache.

### Почему маленький image не автоматически безопасен?

Уязвимость может находиться внутри бинарника или библиотеки приложения.

### Как проверить пользователя без shell?

```bash
docker image inspect <image> --format '{{.Config.User}}'
docker top <container> -eo user,pid,comm
```

