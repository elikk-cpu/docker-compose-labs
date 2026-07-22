# RESULT — Project 08

## Итог

Выполнена лаборатория диагностики Docker и Docker Compose.

Разобраны восемь логически сломанных сценариев:

1. Container immediately exits.
2. Port published to wrong container port.
3. Service uses localhost instead of Docker DNS.
4. Non-root process cannot write.
5. Running container is unhealthy.
6. Fixed container name conflict.
7. Init changes do not apply to an existing PostgreSQL volume.
8. Image or tag cannot be pulled.

Для каждого кейса:

- воспроизведён исходный symptom;
- собран evidence;
- сформулирована и проверена гипотеза;
- найден root cause;
- внесено минимальное исправление;
- проверен исправленный сценарий;
- объяснено, почему случайный restart или prune не устраняет причину.

## Case 01 — Container immediately exits

### Symptom

Контейнер сразу завершался:

```text
Exited (0)
```

### Root cause

Dockerfile запускал одноразовую команду:

```dockerfile
CMD ["python", "-c", "print('container started')"]
```

Команда успешно выполнялась и завершалась с exit code 0.

### Исправление

```dockerfile
CMD ["python", "app.py"]
```

После исправления HTTP-сервис оставался running и возвращал:

```text
HTTP 200
running
```

## Case 02 — Wrong container port

### Symptom

Контейнер был running, но host port не отвечал.

### Root cause

Compose публиковал:

```text
127.0.0.1:8102 -> 5000
```

Приложение слушало внутри контейнера:

```text
0.0.0.0:8000
```

### Исправление

```yaml
ports:
  - "127.0.0.1:8102:8000"
```

После исправления:

```text
HTTP 200
port-ok
```

## Case 03 — Localhost вместо Docker DNS

### Symptom

API выводил:

```text
cannot connect to localhost:5432
Connection refused
```

### Root cause

`localhost` внутри API-контейнера указывал на сам API-контейнер, а database работала в другом контейнере.

### Исправление

```yaml
environment:
  DB_HOST: database
```

После исправления Docker DNS разрешал service name, а API получал:

```text
db-ready
```

## Case 04 — Permissions

### Symptom

Non-root процесс не мог записать:

```text
/data/result.txt
```

### Root cause

Каталог принадлежал `root:root` и имел права `700`, а процесс работал от UID/GID `10001:10001`.

### Исправление

```dockerfile
RUN mkdir /data     && chown 10001:10001 /data     && chmod 700 /data
```

После исправления:

```text
write successful
```

Контейнер завершился с exit code 0, что нормально для одноразовой job.

## Case 05 — Running, но unhealthy

### Symptom

Контейнер оставался running, но health status становился:

```text
unhealthy
```

### Root cause

Healthcheck обращался к несуществующему endpoint:

```text
/readyz
```

Приложение предоставляло:

```text
/healthz
```

### Исправление

Healthcheck был направлен на `/healthz`.

Результат:

```text
status=running health=healthy
```

## Case 06 — Container name conflict

### Symptom

Compose не мог создать контейнер, потому что имя уже было занято вручную созданным контейнером.

### Root cause

В Compose использовался:

```yaml
container_name: docker-lab-fixed-name
```

Container names должны быть уникальны на Docker host.

### Исправление

Директива `container_name` удалена.

Compose автоматически создал:

```text
broken-06-name-conflict-app-1
```

Оба контейнера смогли работать одновременно.

## Case 07 — Stale PostgreSQL volume

### Symptom

После изменения init SQL и пересоздания database-контейнера значение в базе осталось:

```text
first-version
```

### Root cause

Файлы `/docker-entrypoint-initdb.d` выполняются только при первой инициализации пустого PostgreSQL data directory.

Named volume уже содержал существующий database cluster.

### Исправление

Создана отдельная idempotent migration:

```sql
INSERT INTO settings(key, value)
VALUES ('welcome', 'second-version')
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value;
```

После явного применения migration:

```text
welcome | second-version
```

## Case 08 — Pull error

### Symptom

Compose не мог скачать:

```text
localhost:5000/training/missing-image:9.9.9
```

### Root causes

Сначала отсутствовали credentials:

```text
authorization failed: no basic auth credentials
```

После login registry стал доступен, но repository/tag отсутствовал:

```text
not found
manifest unknown
```

### Исправление

Использован существующий reference:

```text
localhost:5000/labuser/hello-registry:0.1.0
```

Pull прошёл успешно.

## Основные команды диагностики

Использовались:

```bash
docker compose ps -a
docker compose logs
docker compose config
docker inspect <container>
docker network inspect <network>
docker volume inspect <volume>
docker image inspect <image>
docker compose exec <service> <command>
curl
```

## Ответы на вопросы

### 1. Почему контейнер может завершиться с exit code 0 и всё равно быть проблемой?

Exit code 0 означает успешное завершение команды.

Для одноразовой job это нормально.

Для web-service это проблема, если процесс должен оставаться запущенным.

### 2. Как различить DNS failure, connection refused и timeout?

DNS failure:

```text
Temporary failure in name resolution
Name or service not known
```

Имя не преобразовалось в IP.

Connection refused:

```text
Connection refused
```

Host/IP доступен, но на порту никто не слушает или соединение активно отклоняется.

Timeout:

```text
timed out
```

Ответ не получен за установленное время. Возможны firewall, route или зависший сервис.

### 3. Как найти реальный внутренний порт?

Нужно проверить:

- команду приложения;
- исходный код;
- logs;
- `docker inspect`;
- активное подключение внутри контейнера;
- `EXPOSE`, понимая, что оно только metadata.

### 4. Как UID/GID влияют на доступ?

Linux проверяет права по числовым UID/GID.

Если процесс работает от UID 10001, а каталог принадлежит UID 0 и имеет `700`, запись будет запрещена.

### 5. Почему running и healthy — разные состояния?

Running означает, что PID 1 контейнера работает.

Healthy означает, что healthcheck успешно проверяет заявленную capability сервиса.

### 6. Почему изменение init.sql не применяется к существующему PostgreSQL volume?

Init scripts выполняются только при создании нового пустого data directory.

Для существующей базы нужны migrations.

### 7. Почему фиксированный `container_name` создаёт конфликты?

Container name уникален на Docker host.

Фиксированное имя мешает параллельным Compose projects и масштабированию.

### 8. Чем pull access denied отличается от отсутствующего tag?

`pull access denied` или `unauthorized` означает проблему authentication/authorization.

`manifest unknown` или `not found` означает, что доступ есть, но repository, tag или digest отсутствует.

## Почему restart и prune не являются диагностикой

Restart повторяет ту же конфигурацию и обычно воспроизводит ту же ошибку.

Prune удаляет ресурсы, но:

- не исправляет Dockerfile;
- не исправляет Compose-конфигурацию;
- не меняет port mapping;
- не меняет credentials;
- не создаёт отсутствующий tag;
- может удалить полезные ресурсы и данные.

Правильный troubleshooting:

1. зафиксировать symptom;
2. собрать evidence;
3. сформулировать гипотезу;
4. проверить её;
5. изменить только root cause;
6. проверить отсутствие регрессии.

## Выполненные критерии

Для всех восьми кейсов созданы:

```text
diagnosis/case-01.md
diagnosis/case-02.md
diagnosis/case-03.md
diagnosis/case-04.md
diagnosis/case-05.md
diagnosis/case-06.md
diagnosis/case-07.md
diagnosis/case-08.md
```

В каждом документе присутствуют:

- symptom;
- команды диагностики;
- root cause;
- минимальное изменение;
- проверка исправления;
- объяснение, почему restart/prune не является анализом.

`git diff --check` проходит без ошибок.

