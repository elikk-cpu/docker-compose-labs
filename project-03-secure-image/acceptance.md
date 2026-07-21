# Критерии приёмки

- Multi-stage build.
- Final image не содержит `go` toolchain.
- `Config.User` не пуст и не `0`/`root`.
- API работает.
- Секретоподобные файлы отсутствуют в image.
- Контейнер стартует с:
  - read-only root filesystem;
  - `cap_drop=ALL`;
  - `no-new-privileges`.
- Приложен scanning report либо честное описание недоступности сканера.

## Проверки

```bash
docker image inspect <image> --format '{{.Config.User}}'
docker history <image>
docker run --rm <image> go version
docker run --rm --read-only --tmpfs /tmp   --cap-drop=ALL   --security-opt no-new-privileges=true   -p 127.0.0.1:<host-port>:8080 <image>
curl -i http://localhost:<host-port>/healthz
docker scout cves <image>
```

Команда `go version` должна завершиться ошибкой, потому что toolchain отсутствует.
