import json
import os
from pathlib import Path

import psycopg
from redis import Redis


def read_secret(env_name: str, default: str = "") -> str:
    file_value = os.getenv(f"{env_name}_FILE")
    if file_value:
        return Path(file_value).read_text(encoding="utf-8").strip()
    return os.getenv(env_name, default)


def postgres_dsn() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'database')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'app')} "
        f"user={os.getenv('POSTGRES_USER', 'app')} "
        f"password={read_secret('POSTGRES_PASSWORD')}"
    )


redis_client = Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)

print("worker waiting", flush=True)
while True:
    _, raw = redis_client.blpop("jobs")
    payload = json.loads(raw)
    with psycopg.connect(postgres_dsn()) as conn:
        conn.execute(
            "INSERT INTO processed_jobs(payload) VALUES (%s)",
            (json.dumps(payload),),
        )
    print(f"processed {payload}", flush=True)
