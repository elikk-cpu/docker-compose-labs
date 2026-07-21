# Критерии приёмки

- Registry требует credentials.
- Registry data хранится в named volume.
- Push без login завершается отказом.
- Login через `--password-stdin` успешен.
- Image можно pull после удаления локальной копии.
- Зафиксированы version tag и digest.
- Разобраны `unauthorized` и `manifest unknown`.

## Проверки

```bash
docker login localhost:5000
docker image inspect localhost:5000/<namespace>/<repo>:<tag>
docker pull localhost:5000/<namespace>/<repo>:<tag>
docker volume ls
curl -i http://localhost:5000/v2/
```
