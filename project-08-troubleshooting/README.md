# Проект 08. Лаборатория поломок

**Сложность:** средне-повышенная  
**Оценка времени:** 6–10 часов

Каждый каталог содержит **запускаемый, синтаксически корректный, но логически
сломанный** сценарий. Твоя задача — не переписать всё, а:

1. воспроизвести симптом;
2. собрать evidence;
3. сформулировать гипотезу;
4. подтвердить root cause;
5. внести минимальное исправление;
6. проверить отсутствие регрессии;
7. описать результат в `diagnosis/`.

## Кейсы

| № | Каталог | Симптом |
|---|---|---|
| 01 | `broken-01-exit` | Container immediately exits |
| 02 | `broken-02-port` | Port published to wrong container port |
| 03 | `broken-03-localhost` | Service uses localhost instead of DNS name |
| 04 | `broken-04-permissions` | Non-root process cannot write |
| 05 | `broken-05-unhealthy` | Running container is unhealthy |
| 06 | `broken-06-name-conflict` | Fixed container name conflict |
| 07 | `broken-07-stale-volume` | Init changes do not apply to old volume |
| 08 | `broken-08-pull-error` | Image/tag cannot be pulled |

Не используй `docker system prune -a` как универсальное «исправление».
