# Проект 09. Финальный стек Junior DevOps

**Сложность:** повышенная  
**Оценка времени:** 10–16 часов

## Архитектура

```text
Browser -> frontend -> backend -> PostgreSQL
                         |
                         +-> Redis queue -> worker -> PostgreSQL

Monitoring profile:
Prometheus -> backend /metrics
Grafana -> Prometheus
```

## Обязательный результат

1. Три собственных Dockerfile.
2. Multi-stage, где он оправдан.
3. Non-root для backend и worker.
4. `.dockerignore` для build contexts.
5. Edge/data networks.
6. Named volumes PostgreSQL и monitoring.
7. Read-only config mount.
8. Compose secret для PostgreSQL password.
9. Healthchecks и `service_healthy`.
10. Dev и production-like overrides.
11. Profiles `tools` и `monitoring`.
12. Restart policies.
13. `cap_drop`, `no-new-privileges`, read-only FS и tmpfs, где применимо.
14. Registry tagging/push/pull.
15. Image scanning.
16. README/runbook и troubleshooting evidence.
17. Все восемь broken-сценариев из `broken/notes.md`.

## Ограничения

- Нельзя публиковать PostgreSQL и Redis наружу в production-like config.
- Нельзя хранить password в image или committed `.env`.
- Нельзя использовать `container_name`.
- Нельзя использовать `latest`.
- Нельзя маскировать readiness обычным `sleep`.
- Нельзя считать `restart: always` заменой healthcheck.

## После выполнения мы научились

Самостоятельно проектировать, собирать, защищать, публиковать и диагностировать
полноценное Docker/Compose-окружение уровня уверенного Junior DevOps.

## Реализованный проект

Итоговая документация:

- [Runbook](RUNBOOK.md)
- [Результат и acceptance](RESULT.md)
- [Диагностика broken-сценариев](diagnosis/)

Статус: завершён production-like Docker Compose stack с registry,
monitoring, security hardening, persistence и troubleshooting evidence.
