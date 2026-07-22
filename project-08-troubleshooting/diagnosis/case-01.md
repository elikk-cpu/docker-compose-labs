# Case 01 — Container immediately exits

## Symptom

После `docker compose up -d` контейнер завершался со статусом:

```text
Exited (0)
```

## Команды диагностики

```bash
docker compose -f broken-01-exit/compose.yaml ps -a
docker compose -f broken-01-exit/compose.yaml logs
docker inspect <container>
```

`docker inspect` показал:

```text
status=exited
exit=0
command=["python","-c","print('container started')"]
```

## Root cause

Команда контейнера выполняла однократный `print()` и успешно завершалась.

Exit code `0` означает, что команда выполнилась без ошибки. Это не означает, что долгоживущий сервис продолжает работать.

Файл `app.py` не запускался.

## Минимальное исправление

Было:

```dockerfile
CMD ["python", "-c", "print('container started')"]
```

Стало:

```dockerfile
CMD ["python", "app.py"]
```

## Проверка исправления

```bash
docker compose -f broken-01-exit/compose.yaml up -d --build
docker compose -f broken-01-exit/compose.yaml ps -a
curl -i http://127.0.0.1:8101/
```

После исправления контейнер остаётся в состоянии `running`.

HTTP-сервис возвращает:

```text
HTTP/1.0 200 OK

running
```

## Почему случайный restart или prune не является анализом

Restart повторно запустил бы ту же однократную команду, которая снова завершилась бы с exit code `0`.

`docker system prune` удалил бы неиспользуемые ресурсы, но не изменил ошибочный `CMD`.

Исправление должно устранять root cause в Dockerfile, а не временно скрывать симптом.
