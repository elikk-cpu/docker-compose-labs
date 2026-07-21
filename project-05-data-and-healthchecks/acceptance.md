# Критерии приёмки

- `docker compose config` проходит.
- Database/Redis/RabbitMQ становятся healthy.
- API стартует после healthy dependencies.
- `/readyz` возвращает 200.
- `POST /jobs` создаёт задачу.
- Worker записывает результат в PostgreSQL.
- `/stats` показывает submitted и processed.
- Данные переживают пересоздание database container.
- RabbitMQ использует не `guest`.

## Проверки

```bash
docker compose config
docker compose up -d --build
docker compose ps
curl -i http://localhost:<api-port>/healthz
curl -i http://localhost:<api-port>/readyz
curl -i -X POST -H "Content-Type: application/json"   -d '{"task":"demo"}' http://localhost:<api-port>/jobs
curl -i http://localhost:<api-port>/stats
docker compose logs worker
docker compose exec database   psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"   -c "SELECT * FROM processed_jobs;"
```
