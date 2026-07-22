# Case 06 — Fixed container name conflict

## Symptom

После ручного запуска контейнера с именем:

```text
docker-lab-fixed-name
```

команда:

```bash
docker compose -f broken-06-name-conflict/compose.yaml up -d
```

не могла создать Compose-контейнер.

Ошибка указывала, что имя контейнера уже занято.

## Команды диагностики

```bash
docker ps --filter name=docker-lab-fixed-name
docker compose -f broken-06-name-conflict/compose.yaml up -d
docker inspect docker-lab-fixed-name
docker compose -f broken-06-name-conflict/compose.yaml config
```

Проверка показала, что контейнер `docker-lab-fixed-name` уже существовал и был создан вручную.

У него отсутствовал Compose label проекта:

```text
com.docker.compose.project
```

В Compose-файле было зафиксировано то же имя:

```yaml
container_name: docker-lab-fixed-name
```

## Root cause

Docker container name должен быть уникальным на одном Docker host.

Ручной контейнер уже занимал имя:

```text
docker-lab-fixed-name
```

Compose пытался создать другой контейнер с тем же именем и получил конфликт.

Фиксированный `container_name` также мешает:

- параллельному запуску нескольких Compose projects;
- масштабированию сервиса;
- автоматическому namespace Compose;
- повторному использованию одного Compose-файла.

## Минимальное исправление

Было:

```yaml
services:
  app:
    image: alpine:3.22.2
    container_name: docker-lab-fixed-name
```

Стало:

```yaml
services:
  app:
    image: alpine:3.22.2
```

Compose самостоятельно создал имя:

```text
broken-06-name-conflict-app-1
```

## Проверка исправления

```bash
docker compose -f broken-06-name-conflict/compose.yaml up -d
docker compose -f broken-06-name-conflict/compose.yaml ps
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

После исправления одновременно работали:

```text
docker-lab-fixed-name
broken-06-name-conflict-app-1
```

## Почему Compose-generated name лучше

Compose включает в имя:

```text
project-service-index
```

Например:

```text
broken-06-name-conflict-app-1
```

Project name создаёт namespace и позволяет запускать одинаковые сервисы в разных проектах без конфликта имён.

## Почему случайный restart или prune не является анализом

Restart не освобождает занятое имя и не меняет `container_name`.

Удаление вручную созданного контейнера временно освободило бы имя, но root cause остался бы в Compose-файле. При следующем конфликте проблема повторилась бы.

`docker system prune` может удалить unrelated resources и не гарантирует устранение конфликта активного контейнера.

Минимальное исправление — удалить фиксированный `container_name` и позволить Compose управлять именованием.
