# Критерии приёмки

- `docker compose config` проходит.
- Все три сервиса running.
- Frontend доступен с хоста.
- Запрос через frontend увеличивает Redis counter.
- Backend резолвит имя `redis`.
- Redis не опубликован на host.
- Frontend не подключён к backend-only network.
- Нет `container_name`.

## Проверки

```bash
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail 100
docker compose exec backend getent hosts redis
curl -i http://localhost:<frontend-port>/
curl -i http://localhost:<frontend-port>/api/counter
```
