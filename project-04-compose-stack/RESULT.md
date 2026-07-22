# RESULT — Project 04

## Итог

Собран Compose-стек:

```text
Host -> frontend:Nginx -> backend:Flask -> redis
```

Сервисы:
- `frontend` — Nginx, статический сайт и reverse proxy;
- `backend` — Flask API под Gunicorn;
- `redis` — внутреннее хранилище счётчика.

Наружу опубликован только frontend:

```text
127.0.0.1:8080 -> frontend:8080
```

## Сети

- `frontend` подключён только к `frontend_net`;
- `backend` подключён к `frontend_net` и `backend_net`;
- `redis` подключён только к `backend_net`.

Это даёт маршрут:

```text
frontend_net: frontend <-> backend
backend_net:  backend  <-> redis
```

Frontend не имеет прямого доступа к Redis.

## Compose-конфигурация

```yaml
services:
  frontend:
    build:
      context: ./frontend
    image: compose-lab-frontend:0.1.0
    ports:
      - "127.0.0.1:8080:8080"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - frontend_net

  backend:
    build:
      context: ./backend
      network: host
    image: compose-lab-backend:0.1.0
    environment:
      REDIS_HOST: redis
      REDIS_PORT: "6379"
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - frontend_net
      - backend_net

  redis:
    image: redis:7.4.2-alpine3.21
    restart: unless-stopped
    networks:
      - backend_net

networks:
  frontend_net:
  backend_net:
```

## Проверки

### Compose config

```bash
docker compose config
```

Конфигурация проходит проверку.

### Запуск

```bash
docker compose up -d --build
docker compose ps
```

Все три сервиса имеют статус `Up`.

### Frontend

```bash
curl -i http://localhost:8080/
```

Результат:

```text
HTTP/1.1 200 OK
```

### Reverse proxy и Redis counter

```bash
curl -i http://localhost:8080/api/counter
```

Результат:

```json
{"counter":1}
```

Повторные запросы увеличивают значение.

### Docker DNS

```bash
docker compose exec backend getent hosts redis
```

Backend успешно резолвит service name `redis`.

### Backend -> Redis

```bash
docker compose exec backend python -c \
"from redis import Redis; r=Redis(host='redis',port=6379); print(r.ping())"
```

Результат:

```text
True
```

### Redis не опубликован на host

```bash
ss -lnt | grep ':6379'
```

Порт `6379` на host отсутствует. Подключение к `127.0.0.1:6379` завершается `Connection refused`.

### Сетевая изоляция

Frontend:

```text
project-04-compose-stack_frontend_net
```

Backend:

```text
project-04-compose-stack_frontend_net
project-04-compose-stack_backend_net
```

Redis:

```text
project-04-compose-stack_backend_net
```

### container_name

В `compose.yaml` не используется `container_name`. Compose автоматически формирует имена контейнеров.

## Проблема сети во время build

При обычной сборке backend команда `pip install` не могла подключиться к PyPI:

```text
Temporary failure in name resolution
```

Проверки показали:

- Ubuntu VM имеет доступ к PyPI;
- bridge-контейнеры не имеют исходящего доступа;
- сборка через host network проходит.

Поэтому для build backend используется:

```yaml
build:
  context: ./backend
  network: host
```

Это относится только к инструкциям `RUN` во время сборки. Запущенный backend остаётся в изолированных Compose-сетях и не использует host network.

## Redis memory overcommit

Для удаления предупреждения Redis применено:

```bash
sudo sysctl -w vm.overcommit_memory=1
```

Постоянная настройка сохранена в:

```text
/etc/sysctl.d/99-redis.conf
```

## Ответы на вопросы

### 1. Чем service name отличается от container name?

Service name — логическое имя в `compose.yaml`, например `redis`. Оно используется внутренним Docker DNS.

Container name — имя конкретного контейнера, например `project-04-compose-stack-redis-1`. Compose формирует его автоматически.

### 2. Почему backend обращается к `redis:6379`, а не `localhost`?

Внутри backend-контейнера `localhost` означает сам backend. Redis работает в другом контейнере, поэтому используется DNS-имя `redis` и порт `6379`.

### 3. Почему Redis не требует `ports`?

`ports` публикует порт на host. Backend и Redis находятся в общей внутренней сети, поэтому backend подключается напрямую к container port Redis.

### 4. Что создаёт Compose автоматически?

Compose создаёт контейнеры, сети, DNS-записи service names, labels, имена ресурсов и связи между сервисами. Images он собирает через `build` или получает через `image`.

### 5. Чем `docker compose exec` отличается от `docker compose run --rm`?

`exec` запускает команду внутри уже работающего контейнера.

`run --rm` создаёт отдельный временный контейнер для разовой команды, а после завершения удаляет его.

### 6. Зачем разделять frontend/backend сети?

Это ограничивает доступ между компонентами. Frontend видит backend, но не Redis. Redis доступен только backend. Такая сегментация уменьшает attack surface и реализует least privilege.

## Команды жизненного цикла

Проверены:

```bash
docker compose up
docker compose up -d
docker compose ps
docker compose logs
docker compose exec
docker compose down
```

## Вывод

Все критерии приёмки выполнены:

- `docker compose config` проходит;
- все три сервиса работают;
- frontend доступен с host;
- counter увеличивается;
- backend резолвит `redis`;
- Redis не опубликован;
- frontend не подключён к backend-only сети;
- `container_name` не используется.

