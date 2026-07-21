$ErrorActionPreference = "Stop"
if (-not $env:REGISTRY_USER -or -not $env:REGISTRY_PASSWORD) {
    throw "Set REGISTRY_USER and REGISTRY_PASSWORD first."
}
New-Item -ItemType Directory -Force -Path auth | Out-Null
docker run --rm --entrypoint htpasswd `
    httpd:2.4-alpine `
    -Bbn $env:REGISTRY_USER $env:REGISTRY_PASSWORD |
    Set-Content -NoNewline -Encoding ascii auth/htpasswd
Write-Host "Created registry/auth/htpasswd"
