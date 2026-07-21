# Проект 04. Первый Compose-стек

**Сложность:** средняя  
**Оценка времени:** 6–8 часов

## Архитектура

```text
Browser -> frontend:Nginx -> backend:Flask -> redis
```

## Задание

1. Создай Dockerfiles frontend и backend.
2. Создай `compose.yaml`.
3. Используй service names как DNS names.
4. Раздели frontend- и backend-сети.
5. Опубликуй наружу только frontend.
6. Передай Redis host/port через environment.
7. Добавь restart policy, подходящую локальному сервису.
8. Проверь `up`, `up -d`, `ps`, `logs`, `exec`, `down`.
9. Докажи, что Redis недоступен с хоста, но доступен backend.
10. Не используй `container_name`.

## После выполнения мы научились

Описывать сервисы, images/build, ports, environment, networks и внутренний DNS
в Compose.

## Где пригодится

Локальные окружения разработки и воспроизводимые интеграционные стенды.
