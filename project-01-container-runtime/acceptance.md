# Критерии приёмки

- Image — `nginx:1.30.4-alpine3.24`.
- Контейнер `landing` находится в `running`.
- `http://localhost:8088/` и `/health.txt` доступны.
- Оба mount-а read-only.
- Контейнер подключён к user-defined bridge network.
- Диагностический контейнер получает `http://landing:8080/health.txt`.
- В сети `none` та же проверка не работает.
- Есть объяснение `stop/start` против удаления и пересоздания.
- Продемонстрировано исчезновение файла из writable layer после удаления.

## Проверки

```bash
docker ps --filter name=landing
docker inspect landing --format '{{.Config.Image}}'
docker inspect landing --format '{{json .Mounts}}'
docker inspect landing --format '{{json .NetworkSettings.Networks}}'
docker logs landing
docker history nginx:1.30.4-alpine3.24
docker stats --no-stream landing
curl -i http://localhost:8088/
curl -i http://localhost:8088/health.txt
```

Самостоятельно составь команду проверки из `curlimages/curl:8.12.1` в своей сети.
