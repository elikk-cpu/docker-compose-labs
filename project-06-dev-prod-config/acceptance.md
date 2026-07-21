# Критерии приёмки

- Default запуск применяет `compose.override.yaml`.
- Prod запускается явным `-f compose.yaml -f compose.prod.yaml`.
- В production отсутствуют bind mounts исходников.
- Adminer не стартует без profile.
- `docker compose config` показывает ожидаемые значения.
- Два project names запускаются без конфликтов.

## Проверки

```bash
docker compose config
docker compose --profile tools config
docker compose -f compose.yaml -f compose.prod.yaml config
docker compose -p dev-a up -d
docker compose -p dev-b up -d
docker compose -p dev-a ps
docker compose -p dev-b ps
```
