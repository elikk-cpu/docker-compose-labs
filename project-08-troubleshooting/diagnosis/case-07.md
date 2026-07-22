# Case 07 — Init changes do not apply to an existing PostgreSQL volume

## Symptom

После первого запуска PostgreSQL значение в таблице было:

```text
welcome | first-version
```

Затем SQL-файл инициализации был изменён с:

```text
first-version
```

на:

```text
second-version
```

После пересоздания database-контейнера без удаления named volume значение в базе осталось прежним:

```text
welcome | first-version
```

## Команды диагностики

```bash
docker compose -f broken-07-stale-volume/compose.yaml ps -a

docker compose -f broken-07-stale-volume/compose.yaml   exec database   psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"   -c "SELECT * FROM settings;"

docker inspect <database-container>

docker volume inspect <database-volume>
```

Использовался named volume:

```text
broken-07-stale-volume_database-data
```

Он был смонтирован в:

```text
/var/lib/postgresql/data
```

## Root cause

Официальный PostgreSQL image выполняет файлы из:

```text
/docker-entrypoint-initdb.d
```

только при первой инициализации пустого каталога данных.

После первого запуска named volume уже содержал PostgreSQL cluster.

При следующих запусках entrypoint обнаруживал существующую базу и не выполнял init SQL повторно.

Изменение `001_init.sql` не является миграцией уже существующей базы.

## Воспроизведение

Первый запуск создал значение:

```text
welcome | first-version
```

После изменения init-файла и пересоздания контейнера без удаления volume:

```bash
docker compose -f broken-07-stale-volume/compose.yaml down
docker compose -f broken-07-stale-volume/compose.yaml up -d
```

значение осталось:

```text
welcome | first-version
```

Это подтвердило, что данные были загружены из существующего volume, а init-файл повторно не запускался.

## Минимальное исправление

Исходный init-файл был возвращён в первоначальное состояние.

Для изменения существующей базы создан отдельный migration-файл:

```sql
INSERT INTO settings(key, value)
VALUES ('welcome', 'second-version')
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value;
```

Миграция была применена явно:

```bash
docker compose -f broken-07-stale-volume/compose.yaml   exec database   psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"   -f /docker-entrypoint-initdb.d/002_update.sql
```

## Проверка исправления

После применения миграции:

```bash
docker compose -f broken-07-stale-volume/compose.yaml   exec database   psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"   -c "SELECT * FROM settings;"
```

результат стал:

```text
welcome | second-version
```

## Когда допустим `down -v`

Удаление volume допустимо, когда:

- это одноразовое локальное окружение;
- данные не нужны;
- требуется полностью чистая инициализация;
- потеря данных явно ожидаема.

Для production или значимых данных `down -v` не является исправлением.

Нужно применять управляемые migrations.

## Почему случайный restart или prune не является анализом

Restart использовал бы тот же существующий PostgreSQL volume.

Init-файл снова не выполнился бы.

`docker system prune` обычно не удаляет используемый named volume и не применяет SQL migration.

Даже принудительное удаление volume уничтожило бы данные вместо корректного обновления схемы.

Root cause устраняется явной миграцией существующей базы.
