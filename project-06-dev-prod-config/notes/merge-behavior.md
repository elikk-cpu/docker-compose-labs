# Что проверить

- scalar values заменяются поздним файлом;
- environment объединяется по ключу;
- volumes сопоставляются по container target;
- command и entrypoint заменяются;
- относительные пути считаются от первого Compose-файла;
- итог всегда смотри через `docker compose config`.
