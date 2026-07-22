# Broken scenario 08 — Registry tag does not exist

## Symptom

Production-like Compose configuration ссылалась на image:

```text
localhost:5000/labuser/final-backend:9.9.9
```

Попытка pull завершалась ошибкой:

```text
localhost:5000/labuser/final-backend:9.9.9: not found
```

## Команды диагностики

```bash
docker compose   -f compose.yaml   -f compose.prod.yaml   -f broken/case-08/compose.broken.yaml   config

docker pull localhost:5000/labuser/final-backend:9.9.9

curl -u "${REGISTRY_USER}:${REGISTRY_PASSWORD}"   http://localhost:5000/v2/labuser/final-backend/tags/list
```

## Evidence

Итоговая Compose-конфигурация содержала:

```text
image: localhost:5000/labuser/final-backend:9.9.9
```

Registry вернул список доступных tags:

```json
{"name":"labuser/final-backend","tags":["1.0.0"]}
```

Tag `9.9.9` отсутствовал.

## Root cause

Repository существовал, authentication работала, но запрошенный version tag не был опубликован в registry.

Это не проблема DNS и не проблема credentials.

Ошибка `not found` появилась после успешного обращения к registry и означала отсутствие manifest для указанного tag.

## Минимальное исправление

Было:

```yaml
services:
  backend:
    image: localhost:5000/labuser/final-backend:9.9.9
```

Стало:

```yaml
services:
  backend:
    image: localhost:5000/labuser/final-backend:1.0.0
```

## Проверка исправления

```bash
docker pull localhost:5000/labuser/final-backend:1.0.0
```

Результат:

```text
Status: Image is up to date
```

Проверка image:

```text
tag=localhost:5000/labuser/final-backend:1.0.0
digest=localhost:5000/labuser/final-backend@sha256:cfb2c54bb2e98e5c9f636b6acf...
user=10001:10001
```

## Почему restart или prune не является исправлением

Restart повторно запросил бы отсутствующий tag `9.9.9`.

Prune не создаёт manifest и не публикует image в registry.

Root cause устраняется использованием существующего version tag либо публикацией нового image под требуемым tag.

