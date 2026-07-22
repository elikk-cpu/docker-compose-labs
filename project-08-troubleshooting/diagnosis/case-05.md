# Case 05 — Running container is unhealthy

## Symptom

Контейнер продолжал работать, но после нескольких healthcheck-проверок получал статус:

```text
unhealthy
```

## Команды диагностики

```bash
docker compose -f broken-05-unhealthy/compose.yaml ps -a
docker inspect <container>
docker inspect <container>   --format '{{range .State.Health.Log}}{{println .ExitCode}}{{println .Output}}{{end}}'
```

Проверка состояния показала:

```text
status=running
health=unhealthy
```

Healthcheck обращался к endpoint:

```text
http://localhost:8000/readyz
```

Приложение предоставляло только:

```text
/healthz
```

Проверка реального endpoint внутри контейнера:

```bash
docker compose -f broken-05-unhealthy/compose.yaml exec app   python -c   "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/healthz').read().decode())"
```

Результат:

```text
ok
```

## Root cause

Healthcheck проверял несуществующий endpoint `/readyz`.

Приложение отвечало на `/healthz`, а запрос к `/readyz` возвращал HTTP 404.

Контейнерный процесс продолжал работать, поэтому состояние контейнера было `running`, но healthcheck регулярно завершался с ошибкой.

## Минимальное исправление

Было:

```yaml
healthcheck:
  test:
    - CMD
    - python
    - -c
    - |
      import urllib.request
      urllib.request.urlopen("http://localhost:8000/readyz", timeout=2)
```

Стало:

```yaml
healthcheck:
  test:
    - CMD
    - python
    - -c
    - |
      import urllib.request
      urllib.request.urlopen("http://localhost:8000/healthz", timeout=2)
```

## Проверка исправления

```bash
docker compose -f broken-05-unhealthy/compose.yaml   up -d --force-recreate

docker compose -f broken-05-unhealthy/compose.yaml   ps

docker inspect <container>   --format 'status={{.State.Status}} health={{.State.Health.Status}}'
```

После исправления:

```text
status=running health=healthy
```

## Почему running и healthy — разные состояния

`running` означает, что главный процесс контейнера не завершился.

`healthy` означает, что команда healthcheck успешно проверяет способность сервиса выполнять ожидаемую функцию.

Процесс может продолжать работать, но приложение может:

- возвращать ошибки;
- не слушать нужный endpoint;
- не завершить инициализацию;
- потерять доступ к зависимостям;
- иметь неверный healthcheck.

## Почему случайный restart или prune не является анализом

Restart запустил бы тот же контейнер с тем же неправильным endpoint `/readyz`.

После нескольких неудачных проверок контейнер снова стал бы `unhealthy`.

`docker system prune` не изменил бы healthcheck в `compose.yaml`.

Root cause устраняется исправлением проверяемого endpoint с `/readyz` на `/healthz`.
