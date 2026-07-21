# Bash, PowerShell и пути

## Переменная текущей директории

Bash / WSL / Git Bash:

```bash
-v "$(pwd)/site:/usr/share/nginx/html:ro"
```

PowerShell:

```powershell
-v "${PWD}/site:/usr/share/nginx/html:ro"
```

Для сложных mounts предпочтительнее `--mount`, где пути читаются яснее.

## curl в PowerShell

Чтобы точно вызвать curl, а не PowerShell-алиас:

```powershell
curl.exe -i http://localhost:8088/
```

Либо:

```powershell
Invoke-WebRequest http://localhost:8088/
```

## Перенос команд

Bash использует `\`, PowerShell — обратный апостроф `` ` ``.
В `RESULT.md` можешь записывать итоговую команду в одну строку, чтобы она была
однозначной.

## Permissions labs

Лаборатории прав спроектированы внутри image и воспроизводятся на Linux containers.
На Docker Desktop используй режим Linux containers.
