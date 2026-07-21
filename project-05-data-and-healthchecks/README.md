# Проект 05. Данные, очереди и готовность сервисов

**Сложность:** средняя  
**Оценка времени:** 6–10 часов

## Архитектура

```text
API -> PostgreSQL
API -> Redis
API -> RabbitMQ -> Worker -> PostgreSQL
```

## Задание

Выполняй проект поэтапно:

1. Подними API и PostgreSQL с named volume.
2. Добавь PostgreSQL healthcheck и `service_healthy`.
3. Докажи persistence после удаления контейнера БД.
4. Добавь Redis с healthcheck.
5. Добавь RabbitMQ и worker.
6. Используй отдельного пользователя RabbitMQ — `guest` между контейнерами запрещён.
7. Настрой healthchecks так, чтобы они проверяли реальные capabilities сервиса.
8. Проверь `/readyz`, постановку задач и обработку worker.
9. Сравни `down` и `down -v`.
10. Воспроизведи проблему: container running, но service not ready.

## Ограничения

- БД, Redis и AMQP-порт RabbitMQ не публикуются наружу без причины.
- Пароли не записываются в Dockerfile.
- Нельзя лечить readiness бесконечным `sleep`.
- Нельзя удалять volume, если задача — сохранить данные.

## После выполнения мы научились

Persistence, healthchecks, readiness, сервисные зависимости, RabbitMQ worker
и диагностика сложного локального стека.
