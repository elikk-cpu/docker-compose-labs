# Case 03 — Service uses localhost instead of Docker DNS

## Symptom

API постоянно выводил:

```text
cannot connect to localhost:5432: [Errno 111] Connection refused
```

Оба контейнера при этом имели состояние `running`.

## Команды диагностики

```bash
docker compose -f broken-03-localhost/compose.yaml ps -a
docker compose -f broken-03-localhost/compose.yaml logs
docker inspect <api-container>
docker compose -f broken-03-localhost/compose.yaml exec api   python -c "import socket; print(socket.gethostbyname('database'))"
```

Переменная окружения API:

```text
DB_HOST=localhost
```

Docker DNS успешно разрешал service name:

```text
database=<internal-ip>
```

Проверка подключения напрямую к service name:

```bash
docker compose -f broken-03-localhost/compose.yaml exec api   python -c   "import socket; s=socket.create_connection(('database',5432),2); print(s.recv(32).decode()); s.close()"
```

Результат:

```text
db-ready
```

## Root cause

Внутри контейнера `localhost` указывает на loopback текущего контейнера.

API и database работают в разных контейнерах, поэтому `localhost:5432` внутри API означает порт `5432` самого API-контейнера.

Database необходимо находить через внутренний Docker DNS по service name:

```text
database
```

## Минимальное исправление

Было:

```yaml
environment:
  DB_HOST: localhost
```

Стало:

```yaml
environment:
  DB_HOST: database
```

## Проверка исправления

```bash
docker compose -f broken-03-localhost/compose.yaml   up -d --force-recreate api

docker compose -f broken-03-localhost/compose.yaml   logs api

docker compose -f broken-03-localhost/compose.yaml   ps
```

После исправления API выводит:

```text
db-ready
db-ready
db-ready
```

Оба контейнера остаются в состоянии `running`.

## Как различить DNS failure, connection refused и timeout

### DNS failure

Пример:

```text
Temporary failure in name resolution
Name or service not known
```

Имя не удалось преобразовать в IP-адрес.

Проверки:

```bash
getent hosts <service-name>
python -c "import socket; print(socket.gethostbyname('<service-name>'))"
```

### Connection refused

Пример:

```text
[Errno 111] Connection refused
```

IP-адрес доступен, но на указанном порту никто не слушает либо соединение активно отклоняется.

В этом кейсе API обращался к своему `localhost:5432`, где сервис отсутствовал.

### Timeout

Пример:

```text
timed out
```

Пакеты не получили ответа за установленное время.

Возможные причины:

- firewall;
- неправильный маршрут;
- недоступный host;
- зависший сервис;
- пакеты молча отбрасываются.

## Почему случайный restart или prune не является анализом

Restart пересоздал бы API с той же переменной:

```text
DB_HOST=localhost
```

Ошибка повторилась бы.

`docker system prune` не исправил бы неверный адрес зависимости в Compose-конфигурации.

Root cause устраняется заменой `localhost` на service name `database`.
