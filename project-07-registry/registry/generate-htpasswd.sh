#!/usr/bin/env sh
set -eu
mkdir -p auth
docker run --rm --entrypoint htpasswd \
  httpd:2.4-alpine \
  -Bbn "${REGISTRY_USER:?set REGISTRY_USER}" \
  "${REGISTRY_PASSWORD:?set REGISTRY_PASSWORD}" > auth/htpasswd
chmod 600 auth/htpasswd
echo "Created registry/auth/htpasswd"
