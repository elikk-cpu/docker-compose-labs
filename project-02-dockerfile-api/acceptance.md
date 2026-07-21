# Критерии приёмки

- `Dockerfile` и `.dockerignore` существуют.
- Image имеет осмысленный versioned tag.
- Build context не содержит `.git`, `.env`, virtualenv и bytecode.
- Повторная сборка использует cache для dependencies.
- Контейнер остаётся running.
- `/healthz` отвечает 200.
- `/api/info` содержит ожидаемую версию.
- Процесс слушает `0.0.0.0` внутри контейнера.
- Команда запуска записана в exec-форме.

## Проверки

```bash
docker build --progress=plain --build-arg APP_VERSION=0.1.0 -t lab-api:0.1.0 .
docker history lab-api:0.1.0
docker image inspect lab-api:0.1.0
curl -i http://localhost:<host-port>/healthz
curl -i http://localhost:<host-port>/api/info
```
