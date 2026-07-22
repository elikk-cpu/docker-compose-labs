# Broken scenario 03 — PostgreSQL volume keeps old data

## Symptom

После первого запуска в базе было:

```text
release | first-version
```

Init SQL был изменён на:

```text
release | second-version
```

После пересоздания database-контейнера без удаления named volume значение осталось прежним:

```text
release | first-version
```

## Команды диагностики

```bash
docker compose   -p final-broken-03   -f compose.yaml   -f broken/case-03/compose.broken.yaml   ps -a

docker compose   -p final-broken-03   -f compose.yaml   -f broken/case-03/compose.broken.yaml   exec database   psql -U app -d app   -c "SELECT * FROM settings;"

docker inspect <database-container>
docker volume inspect <postgres-volume>
```

## Evidence

Первое значение:

```text
release | first-version
```

После изменения init-файла и пересоздания контейнера без удаления volume:

```text
release | first-version
```

Named volume:

```text
final-broken-03_postgres_data
```

## Root cause

Файлы из:

```text
/docker-entrypoint-initdb.d
```

выполняются только при первой инициализации пустого PostgreSQL data directory.

Named volume уже содержал существующий database cluster, поэтому изменённый init SQL повторно не выполнялся.

Изменение init-файла не является миграцией существующей базы.

## Минимальное исправление

Создан отдельный migration-файл:

```sql
INSERT INTO settings(key, value)
VALUES ('release', 'second-version')
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value;
```

Миграция применена явно:

```bash
docker compose   -p final-broken-03   -f compose.yaml   -f broken/case-03/compose.broken.yaml   exec database   psql -U app -d app   -f /docker-entrypoint-initdb.d/003_update.sql
```

## Проверка исправления

После применения migration:

```text
release | second-version
```

## Почему restart или prune не является исправлением

Restart снова использовал бы существующий named volume.

Init SQL повторно не выполнился бы.

Удаление volume через `down -v` уничтожило бы данные вместо корректного обновления базы.

Root cause устраняется управляемой migration.
