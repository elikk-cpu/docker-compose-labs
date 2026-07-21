# Проект 03. Компактный и безопасный image

**Сложность:** начально-средняя  
**Оценка времени:** 5–8 часов

## Задание

Преобразуй `Dockerfile.insecure` в production-oriented image:

1. Multi-stage build.
2. Final image без Go compiler и исходников.
3. Non-root пользователь с явным UID/GID.
4. `.dockerignore`, исключающий secrets и артефакты.
5. Работа с `--read-only` и отдельным writable tmpfs при необходимости.
6. Runtime hardening: `--cap-drop=ALL` и `no-new-privileges`.
7. Сравнение размера и `docker history`.
8. Scanning через Docker Scout или другой сканер.
9. Проверка `/healthz` и `/api/info`.

## Ограничения

- Нельзя использовать финальный builder image.
- Нельзя класть секреты в ARG, ENV, COPY или layer.
- Нельзя запускать процесс от root.
- Не требуй `/bin/sh` в final image: минимальный runtime может не иметь shell.

## Ты создаёшь

`Dockerfile`, `.dockerignore`, `RESULT.md`.

## После выполнения мы научились

Multi-stage build, non-root, least privilege, image scanning, анализ размера
и проектирование минимального runtime.

## Где пригодится

Production images, CI/CD, security review и уменьшение времени pull/push.
