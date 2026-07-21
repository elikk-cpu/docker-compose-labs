# docker-compose-labs

Практический маршрут по Docker и Docker Compose до уровня уверенного Junior DevOps.

Это **starter kit, а не набор готовых решений**. Код учебных приложений и намеренно
сломанные сценарии уже подготовлены. Dockerfile, Compose-конфигурации и отчёты,
которые являются сутью задания, ты создаёшь или исправляешь самостоятельно.

## Маршрут

| № | Каталог | Проект | Основной результат |
|---|---|---|---|
| 01 | `project-01-container-runtime` | Контейнер как runtime-единица | Уверенный `docker run`, mounts, ports, networks и диагностика |
| 02 | `project-02-dockerfile-api` | Первый Dockerfile | Контейнеризация HTTP API, cache и `.dockerignore` |
| 03 | `project-03-secure-image` | Безопасный production image | Multi-stage, non-root, scanning и hardening |
| 04 | `project-04-compose-stack` | Первый Compose-стек | Frontend + backend + Redis, service DNS |
| 05 | `project-05-data-and-healthchecks` | Данные и readiness | PostgreSQL + Redis + RabbitMQ + worker |
| 06 | `project-06-dev-prod-config` | Dev/prod-конфигурации | Override-файлы, profiles и merge behavior |
| 07 | `project-07-registry` | Registry | Login, tagging, push/pull и protected local registry |
| 08 | `project-08-troubleshooting` | Лаборатория поломок | Системная диагностика восьми неисправностей |
| 09 | `project-09-final-stack` | Финальный стек | Полный Junior DevOps Docker/Compose-проект |

Проходи проекты строго последовательно.

## Общие правила

1. Не используй `latest`.
2. Не храни реальные секреты в Git или image.
3. Не используй `--privileged`, если задание прямо этого не требует.
4. Не исправляй контейнер вручную через `docker exec` как постоянное решение.
5. Для Compose всегда проверяй итог через `docker compose config`.
6. Документируй не только команды, но и причины решений.
7. `RESULT.md` должен коммититься — он намеренно **не добавлен** в `.gitignore`.
8. Проверяй, что важные данные переживают пересоздание контейнера.
9. Публикуй наружу только необходимые порты.
10. Сначала ищи root cause, затем исправляй.

## Git workflow

```bash
git init -b main
git add .
git commit -m "init: add docker-compose-labs starter kit"

git switch -c project-01-container-runtime
```

Делай небольшие содержательные коммиты:

```text
project-01: add reproducible runtime command
project-01: document port mapping failure
project-02: optimize dependency cache
project-03: switch to multi-stage non-root image
```

После приёмки проекта:

```bash
git switch main
git merge project-01-container-runtime
git tag project-01-complete
```

## Как сдавать проект

1. Создай `RESULT.md` на основе `RESULT_TEMPLATE.md`.
2. Приложи релевантный вывод проверок из `acceptance.md`.
3. Не вставляй огромный необработанный `docker inspect`: используй `--format`
   или приложи только нужные секции.
4. Ответь на вопросы из `questions.md`.
5. Укажи места, в которых сомневаешься.

## Поддерживаемые терминалы

Команды в заданиях ориентированы на Bash/WSL/Git Bash. Для PowerShell смотри
[`docs/SHELLS.md`](docs/SHELLS.md).

## Быстрая проверка starter kit

```bash
python scripts/validate_repo.py
```

## Прогресс

- [ ] Project 01
- [ ] Project 02
- [ ] Project 03
- [ ] Project 04
- [ ] Project 05
- [ ] Project 06
- [ ] Project 07
- [ ] Project 08
- [ ] Project 09
