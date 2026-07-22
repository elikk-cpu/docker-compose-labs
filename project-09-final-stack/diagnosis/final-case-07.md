# Broken scenario 07 — Worker runs as root

## Symptom

Worker успешно запускался и обрабатывал задачи, но процесс внутри контейнера работал от root:

```text
uid=0(root) gid=0(root)
```

Контейнер мог оставаться healthy, поэтому проблема не обнаруживалась обычной проверкой доступности сервиса.

## Broken configuration

```yaml
services:
  worker:
    user: "0:0"
```

Эта настройка переопределяла non-root пользователя, заданного в Dockerfile.

## Команды диагностики

```bash
docker compose   -p final-broken-07   -f compose.yaml   -f compose.prod.yaml   -f broken/case-07/compose.broken.yaml   exec -T worker id

docker inspect final-broken-07-worker-1   --format 'configured_user={{.Config.User}}'

docker top final-broken-07-worker-1   -eo user,pid,ppid,comm,args
```

## Root cause

Compose override принудительно запускал worker с UID/GID `0:0`.

Настройка `user` из Compose имеет приоритет над `USER 10001:10001` в image.

Работа от root увеличивает последствия возможной уязвимости приложения или зависимостей.

## Минимальное исправление

Было:

```yaml
services:
  worker:
    user: "0:0"
```

Стало:

```yaml
services:
  worker:
    user: "10001:10001"
```

Также допустимо полностью удалить `user` из Compose и использовать пользователя, заданного в Dockerfile.

## Проверка исправления

```text
uid=10001(app) gid=10001(app)
configured_user=10001:10001
status=running
health=healthy
```

Worker продолжил подключаться к Redis и PostgreSQL после перехода на non-root.

## Почему restart или prune не является исправлением

Restart снова запускал бы контейнер с `user: "0:0"`.

Prune не изменяет runtime user в Compose-конфигурации.

Root cause устраняется удалением root override или явным возвратом UID/GID `10001:10001`.
