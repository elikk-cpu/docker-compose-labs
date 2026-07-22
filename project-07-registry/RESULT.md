# RESULT — Project 07

## Итог

Собран и опубликован versioned Docker image в защищённый локальный registry.

Полное имя image:

```text
localhost:5000/labuser/hello-registry:0.1.0
```

Digest:

```text
sha256:687db7cfc7aad32b3a74e4606be1df97d8fb1258280ef9e975f835f3d1f07465
```

Tag `latest` не использовался.

## Архитектура

```text
Docker client
     |
     | Basic Auth
     v
localhost:5000
     |
     v
registry:3
     |
     v
named volume registry_data
```

Registry опубликован только на localhost:

```text
127.0.0.1:5000
```

## Image

Image собран на базе:

```text
python:3.13.14-slim-bookworm
```

Приложение запускается под Gunicorn и работает от non-root пользователя:

```text
10001:10001
```

Version label:

```text
org.opencontainers.image.version=0.1.0
```

## Полное имя image

Полное reference:

```text
registry/namespace/repository:tag
```

В проекте:

```text
localhost:5000/labuser/hello-registry:0.1.0
```

Части:

- registry — `localhost:5000`;
- namespace — `labuser`;
- repository — `hello-registry`;
- tag — `0.1.0`.

## Registry

Использован image:

```text
registry:3
```

Registry использует:

- Basic Auth;
- htpasswd;
- read-only config mount;
- read-only htpasswd mount;
- named volume для данных.

Compose volume:

```yaml
volumes:
  registry_data:
```

Registry data хранится в:

```text
/var/lib/registry
```

## Authentication

Credentials находятся в `.env` и не коммитятся.

Файл:

```text
registry/auth/htpasswd
```

также исключён из Git.

Login выполнен через:

```bash
printf '%s' "$REGISTRY_PASSWORD" |
  docker login "$REGISTRY_HOST"     --username "$REGISTRY_USER"     --password-stdin
```

Пароль не передавался через `-p`.

## Push без login

Перед проверкой выполнен logout:

```bash
docker logout localhost:5000
```

Push без login завершился ошибкой:

```text
authorization failed: no basic auth credentials
```

Это подтверждает, что registry требует authentication.

## Успешный push

После успешного login выполнен:

```bash
docker push localhost:5000/labuser/hello-registry:0.1.0
```

Tag появился в Registry API:

```text
0.1.0
```

## Pull после удаления локального image

Локальные references были удалены.

После этого выполнен:

```bash
docker pull localhost:5000/labuser/hello-registry:0.1.0
```

Image был успешно восстановлен из registry.

Проверка приложения после pull:

```text
HTTP/1.1 200 OK
{"status":"ok"}
```

## Digest

Зафиксированный digest:

```text
sha256:687db7cfc7aad32b3a74e4606be1df97d8fb1258280ef9e975f835f3d1f07465
```

После остановки и пересоздания registry container image снова был скачан.

Digest не изменился.

Различались только repository prefixes в выводе:

```text
hello-registry@sha256:...
localhost:5000/labuser/hello-registry@sha256:...
```

Значение после `@` осталось одинаковым.

## Registry persistence

Registry container был удалён через:

```bash
docker compose down
```

Named volume сохранился.

После повторного запуска registry image `0.1.0` остался доступен для pull.

Это подтверждает, что registry data хранится не в writable layer container, а в named volume.

## Неверные credentials

Login с неправильным паролем завершился ошибкой authentication.

Это ошибка доступа: registry не подтвердил identity клиента.

## Несуществующий tag

Попытка pull:

```text
localhost:5000/labuser/hello-registry:9.9.9
```

завершилась:

```text
manifest unknown
```

Registry доступен и authentication успешна, но указанный manifest/tag отсутствует.

## `unauthorized` и `manifest unknown`

### `unauthorized`

Означает проблему authentication или authorization.

Причины:

- login не выполнен;
- неверный username/password;
- credentials не подходят registry;
- у пользователя нет прав.

### `manifest unknown`

Означает, что registry доступен и запрос принят, но запрошенного tag или digest нет в repository.

## Почему tag не гарантирует неизменность

Tag — изменяемая ссылка.

Один и тот же tag можно переназначить на новый image manifest.

Например, `0.1.0` технически можно push повторно с другим содержимым.

## Что гарантирует digest

Digest является content-addressed identifier manifest.

Если digest совпадает, manifest image совпадает.

Для точного и воспроизводимого запуска используют:

```text
repository@sha256:...
```

## Почему registry volume не является backup

Volume даёт persistence, но не является независимой резервной копией.

Volume может быть:

- случайно удалён;
- повреждён;
- потерян вместе с Docker host;
- затронут ошибкой storage или filesystem.

Backup должен храниться отдельно и иметь проверенную процедуру восстановления.

## Что делает `docker tag`

`docker tag` не копирует слои image.

Команда создаёт дополнительную локальную reference на существующий image:

```bash
docker tag source:tag registry/namespace/repository:tag
```

После этого image можно push в указанный registry.

## Выполненные критерии

- Registry требует credentials.
- Используется Basic Auth.
- Credentials не коммитятся.
- `htpasswd` не коммитится.
- Registry data хранится в named volume.
- Push без login завершился отказом.
- Login выполнен через `--password-stdin`.
- Использован version tag `0.1.0`.
- `latest` не использовался.
- Image успешно опубликован.
- Локальный image удалён.
- Image успешно скачан обратно.
- Pulled image успешно запущен.
- Зафиксирован digest.
- Digest сохранился после пересоздания registry container.
- Проверены неверные credentials.
- Проверен `manifest unknown`.

## Ответы на вопросы

### 1. Из каких частей состоит полное имя image?

```text
registry/namespace/repository:tag
```

Также вместо tag можно использовать digest:

```text
registry/namespace/repository@sha256:...
```

### 2. Что делает `docker tag`?

Создаёт новое имя/reference для существующего локального image. Слои не копируются.

### 3. Почему tag не гарантирует неизменность?

Tag можно переназначить на другой manifest повторным push.

### 4. Что гарантирует digest?

Digest однозначно идентифицирует содержимое manifest.

### 5. Почему registry volume не является backup?

Volume находится на том же Docker host и может быть потерян вместе с ним. Backup должен быть отдельной копией.

### 6. Чем `unauthorized` отличается от `manifest unknown`?

`unauthorized` — проблема доступа.

`manifest unknown` — repository доступен, но tag или digest отсутствует.

### 7. Почему пароль нельзя передавать через `docker login -p`?

Пароль может попасть в shell history, process list, logs или audit trail.

`--password-stdin` передаёт пароль через stdin и уменьшает риск утечки.

