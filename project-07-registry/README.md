# Проект 07. Registry и публикация images

**Сложность:** средняя  
**Оценка времени:** 4–6 часов

## Задание

1. Собери versioned image.
2. Запусти локальный registry с basic auth и persistent volume.
3. Создай `htpasswd` через предоставленный helper.
4. Проверь отказ push без login.
5. Выполни `docker login` через `--password-stdin`.
6. Подготовь полное image reference с registry/namespace/repository:tag.
7. Выполни push, удали локальный image и pull обратно.
8. Проверь неверный tag (`manifest unknown`) и неверные credentials.
9. Зафиксируй digest.
10. Дополнительно повтори workflow в private Docker Hub repository, если он есть.

## Ограничения

- Registry должен требовать authentication.
- Credentials и htpasswd не коммитятся.
- Пароль не передаётся флагом `-p`.
- Не используй `latest`.

## После выполнения мы научились

Image references, login/tag/push/pull, защищённому local registry, persistence
и диагностике auth/tag errors.
