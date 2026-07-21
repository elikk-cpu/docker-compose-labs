# Критерии приёмки

- Все Compose-файлы проходят `docker compose config`.
- Core stack становится healthy.
- Frontend выполняет API requests.
- Job проходит Redis queue и появляется в PostgreSQL.
- PostgreSQL data сохраняется после пересоздания.
- Secret доступен только нужным сервисам.
- Backend/worker non-root.
- Database/Redis не опубликованы наружу в production-like config.
- Monitoring не стартует без profile и работает с profile.
- Grafana datasource provisioned.
- Images имеют versioned registry tags.
- Приложены scan reports.
- Broken scenarios воспроизведены и документированы.

## Проверки

```bash
docker compose config
docker compose -f compose.yaml -f compose.prod.yaml config
docker compose up -d --build --wait
docker compose ps
curl -i http://localhost:<frontend-port>/api/info
curl -i -X POST -H "Content-Type: application/json"   -d '{"task":"acceptance"}'   http://localhost:<frontend-port>/api/jobs
curl -i http://localhost:<frontend-port>/api/jobs
docker compose --profile monitoring up -d
docker compose exec backend id
docker compose exec worker id
docker scout cves <backend-image>
```
