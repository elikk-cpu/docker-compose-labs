# Критерии приёмки

Для каждого кейса в `diagnosis/case-NN.md` должны быть:

- исходный symptom;
- команды диагностики;
- root cause;
- минимальное изменение;
- проверка исправления;
- объяснение, почему случайный restart/prune не является анализом.

Основной набор:

```bash
docker compose ps -a
docker compose logs
docker compose config
docker inspect <container>
docker network inspect <network>
docker volume inspect <volume>
```
