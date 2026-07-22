# Case 02 — Port published to wrong container port

## Symptom

Контейнер имел состояние `running`, но запрос:

```bash
curl http://localhost:8102
```

не получал ответ.

## Команды диагностики

```bash
docker compose -f broken-02-port/compose.yaml ps -a
docker compose -f broken-02-port/compose.yaml logs
docker inspect <container>
docker exec <container> python -c "..."
```

`docker compose ps` показывал публикацию:

```text
127.0.0.1:8102 -> 5000/tcp
```

При этом приложение внутри контейнера слушало:

```text
0.0.0.0:8000
```

Проверка внутреннего порта:

```bash
docker exec <container>   python -c   "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000').read().decode())"
```

Результат:

```text
port-ok
```

## Root cause

В `compose.yaml` был указан неверный container port.

Было:

```yaml
ports:
  - "127.0.0.1:8102:5000"
```

Приложение не слушало порт `5000`. Оно слушало порт `8000`.

Публикация порта не изменяет порт приложения внутри контейнера. Она только перенаправляет host port на указанный container port.

## Минимальное исправление

Было:

```yaml
ports:
  - "127.0.0.1:8102:5000"
```

Стало:

```yaml
ports:
  - "127.0.0.1:8102:8000"
```

## Проверка исправления

```bash
docker compose -f broken-02-port/compose.yaml up -d --force-recreate
docker compose -f broken-02-port/compose.yaml ps
curl -i http://127.0.0.1:8102/
```

После исправления Compose показывает:

```text
127.0.0.1:8102 -> 8000/tcp
```

HTTP-запрос возвращает:

```text
HTTP/1.0 200 OK

port-ok
```

## Почему случайный restart или prune не является анализом

Restart пересоздал бы контейнер с тем же ошибочным port mapping:

```text
8102 -> 5000
```

Проблема повторилась бы.

`docker system prune` удалил бы неиспользуемые ресурсы, но не исправил бы неверное значение в `compose.yaml`.

Root cause находился в конфигурации публикации порта, поэтому исправление должно быть минимальным изменением container port с `5000` на `8000`.
