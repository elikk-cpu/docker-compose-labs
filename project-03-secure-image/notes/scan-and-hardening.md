# Что намеренно плохо в Dockerfile.insecure

- Build toolchain остаётся в final image.
- Процесс запускается как root.
- В build context легко включить `secrets/`.
- Image не рассчитан на read-only root filesystem.
- Нет scanning и анализа слоёв.
