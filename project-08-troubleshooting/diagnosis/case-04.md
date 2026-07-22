# Case 04 — Non-root process cannot write

## Symptom

Контейнер завершался с ошибкой:

```text
PermissionError
```

при попытке записать файл:

```text
/data/result.txt
```

## Команды диагностики

```bash
docker compose -f broken-04-permissions/compose.yaml ps -a
docker compose -f broken-04-permissions/compose.yaml logs
docker inspect <container>
docker run --rm --entrypoint sh broken-04-permissions-writer -c 'id; ls -ldn /data'
```

Проверка показала:

```text
uid=10001(app) gid=10001(app)
drwx------ 2 0 0 ... /data
```

Процесс работал от UID/GID `10001:10001`, а каталог `/data` принадлежал `root:root` и имел права `700`.

## Root cause

Права `700` разрешают доступ только владельцу каталога.

Владельцем `/data` был root:

```text
UID 0
GID 0
```

Приложение работало от:

```text
UID 10001
GID 10001
```

Поэтому non-root процесс не мог создать `/data/result.txt`.

## Минимальное исправление

Было:

```dockerfile
RUN mkdir /data && chmod 700 /data
```

Стало:

```dockerfile
RUN mkdir /data     && chown 10001:10001 /data     && chmod 700 /data
```

## Проверка исправления

```bash
docker compose -f broken-04-permissions/compose.yaml up -d --build
docker compose -f broken-04-permissions/compose.yaml ps -a
docker compose -f broken-04-permissions/compose.yaml logs
```

Логи после исправления:

```text
write successful
```

Контейнер завершился:

```text
Exited (0)
```

В этом кейсе это ожидаемо: writer является одноразовой задачей и завершает работу после успешной записи.

Права каталога после исправления:

```text
uid=10001(app) gid=10001(app)
drwx------ 2 10001 10001 ... /data
```

## Как UID/GID влияют на доступ

Linux проверяет права по числовым UID и GID.

Имя пользователя внутри контейнера вторично. Важны именно значения:

```text
10001:10001
```

Если mounted directory или файл принадлежит другому UID/GID и не предоставляет подходящих прав группе или остальным, процесс получит `Permission denied`.

## Почему случайный restart или prune не является анализом

Restart повторно запустил бы контейнер с теми же владельцем и правами `/data`.

Ошибка записи повторилась бы.

`docker system prune` не исправил бы ownership внутри image.

Root cause устраняется настройкой владельца каталога под UID/GID runtime-пользователя.
