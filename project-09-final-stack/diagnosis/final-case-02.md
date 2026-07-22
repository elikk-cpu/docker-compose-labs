# Broken scenario 02 — Incorrect frontend proxy target port

## Symptom

Главная страница frontend открывалась, но запрос:

```bash
curl http://127.0.0.1:8182/api/info
```

возвращал:

```text
HTTP/1.1 502 Bad Gateway
```

## Команды диагностики

```bash
docker compose   -p final-broken-02   -f compose.yaml   -f compose.prod.yaml   -f broken/case-02/compose.broken.yaml   ps -a

docker compose   -p final-broken-02   -f compose.yaml   -f compose.prod.yaml   -f broken/case-02/compose.broken.yaml   logs frontend

docker exec <frontend-container>   wget -qO- http://backend:5000/healthz

docker exec <frontend-container>   wget -qO- http://backend:8000/healthz
```

## Evidence

Проверка неправильного порта:

```text
backend:5000 failed
```

Проверка реального порта backend:

```text
{"status":"alive"}
```

В сломанной конфигурации Nginx было:

```nginx
proxy_pass http://backend:5000;
```

Backend фактически слушал:

```text
0.0.0.0:8000
```

## Root cause

Frontend успешно разрешал service name `backend`, но подключался к неправильному container port.

Docker DNS работал корректно. Ошибка находилась не в имени сервиса, а в target port reverse proxy.

## Минимальное исправление

Было:

```nginx
proxy_pass http://backend:5000;
```

Стало:

```nginx
proxy_pass http://backend:8000;
```

## Проверка исправления

```bash
FRONTEND_PORT=8182 docker compose   -p final-broken-02   -f compose.yaml   -f compose.prod.yaml   -f broken/case-02/compose.fixed.yaml   up -d --wait

curl -i http://127.0.0.1:8182/api/info
```

Результат:

```text
HTTP/1.1 200 OK
```

Проверка конфигурации внутри frontend:

```text
proxy_pass http://backend:8000;
```

Все core-сервисы стали healthy.

## Почему restart или prune не является исправлением

Restart снова загрузил бы конфигурацию:

```nginx
proxy_pass http://backend:5000;
```

и Nginx продолжил бы возвращать `502 Bad Gateway`.

Prune не исправил бы target port в конфигурации Nginx.

Root cause устраняется заменой порта `5000` на фактический внутренний порт backend `8000`.
