# Проект 06. Dev/prod-конфигурации

**Сложность:** средняя  
**Оценка времени:** 5–8 часов

## Задание

Создай:

- `compose.yaml` — общая база;
- `compose.override.yaml` — локальная разработка;
- `compose.prod.yaml` — production-like запуск.

Требования:

1. Dev использует bind mount кода и debug environment.
2. Production использует собранный image и не монтирует исходники.
3. Adminer запускается только через profile `tools`.
4. Database port доступен с хоста только в dev и только на localhost.
5. Конфиг подключается read-only.
6. Проверь precedence `.env`, `env_file`, `environment` и CLI.
7. Для каждого набора файлов сохрани результат `docker compose config`.
8. Используй разные project names для двух параллельных окружений.

## После выполнения мы научились

Override-файлам, merge behavior, profiles, env precedence и параллельным
Compose-проектам.
