# Case 08 — Image or tag cannot be pulled

## Symptom

Команда:

```bash
docker compose -f broken-08-pull-error/compose.yaml pull
```

не могла скачать image:

```text
localhost:5000/training/missing-image:9.9.9
```

## Команды диагностики

```bash
docker compose -f broken-08-pull-error/compose.yaml config
docker compose -f broken-08-pull-error/compose.yaml pull
curl -i http://localhost:5000/v2/
docker login localhost:5000
curl -u "$REGISTRY_USER:$REGISTRY_PASSWORD"   http://localhost:5000/v2/_catalog
curl -u "$REGISTRY_USER:$REGISTRY_PASSWORD"   http://localhost:5000/v2/labuser/hello-registry/tags/list
```

## Первый root cause — authentication

До login pull завершался ошибкой:

```text
pull access denied
authorization failed: no basic auth credentials
```

Проверка Registry API без credentials:

```text
HTTP/1.1 401 Unauthorized
```

Это подтверждало, что registry работает, но требует authentication.

## Проверка credentials

Login был выполнен безопасно через stdin:

```bash
printf '%s' "$REGISTRY_PASSWORD"   | docker login localhost:5000       --username "$REGISTRY_USER"       --password-stdin
```

Результат:

```text
Login Succeeded
```

## Второй root cause — отсутствующий repository/tag

После успешного login ошибка изменилась:

```text
localhost:5000/training/missing-image:9.9.9: not found
```

Это означает, что authentication уже успешна, но указанный repository или tag отсутствует.

Registry catalog показал существующий repository:

```json
{"repositories":["labuser/hello-registry"]}
```

Список tags:

```json
{"name":"labuser/hello-registry","tags":["0.1.0"]}
```

## Минимальное исправление

Было:

```yaml
services:
  missing:
    image: localhost:5000/training/missing-image:9.9.9
```

Стало:

```yaml
services:
  missing:
    image: localhost:5000/labuser/hello-registry:0.1.0
```

## Проверка исправления

```bash
docker compose -f broken-08-pull-error/compose.yaml pull
```

Результат:

```text
Image localhost:5000/labuser/hello-registry:0.1.0 Pulled
```

Проверка image:

```bash
docker image inspect   localhost:5000/labuser/hello-registry:0.1.0   --format 'tags={{json .RepoTags}} digest={{index .RepoDigests 0}}'
```

Результат:

```text
tags=["localhost:5000/labuser/hello-registry:0.1.0"]
digest=localhost:5000/labuser/hello-registry@sha256:687db7cfc7aad32b3a74e4606be1df97d8fb1258280ef9e975f835f3d1f07465
```

## Чем `pull access denied` отличается от отсутствующего tag

### Pull access denied / unauthorized

Означает проблему доступа:

- login не выполнен;
- credentials неверны;
- нет прав на repository;
- registry требует authentication.

### Manifest unknown / not found

Означает, что registry доступен и authentication прошла, но:

- repository не существует;
- tag не существует;
- digest не существует.

В этом кейсе после login ошибка изменилась с access denied на `not found`, что помогло отделить проблему authentication от неправильного image reference.

## Почему случайный restart или prune не является анализом

Restart не меняет image reference и credentials.

Compose снова попытался бы скачать:

```text
localhost:5000/training/missing-image:9.9.9
```

`docker system prune` не создаёт отсутствующий repository/tag и не выполняет login.

Root cause устраняется двумя точными действиями:

1. выполнить authentication;
2. использовать существующий repository и version tag.
