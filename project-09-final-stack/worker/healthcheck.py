import os
from pathlib import Path

import psycopg
from redis import Redis


def read_secret(env_name: str) -> str:
    path = os.getenv(f"{env_name}_FILE")
    if path:
        return Path(path).read_text(encoding="utf-8").strip()
    return os.getenv(env_name, "")


Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
).ping()

dsn = (
    f"host={os.getenv('POSTGRES_HOST', 'database')} "
    f"port={os.getenv('POSTGRES_PORT', '5432')} "
    f"dbname={os.getenv('POSTGRES_DB', 'app')} "
    f"user={os.getenv('POSTGRES_USER', 'app')} "
    f"password={read_secret('POSTGRES_PASSWORD')}"
)

with psycopg.connect(dsn, connect_timeout=2) as connection:
    connection.execute("SELECT 1")
