import json
import os
from pathlib import Path

import psycopg
import yaml
from flask import Flask, jsonify, request
from prometheus_client import Counter, generate_latest
from redis import Redis

app = Flask(__name__)
REQUESTS = Counter("training_http_requests_total", "HTTP requests", ["endpoint"])


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


def redis_client() -> Redis:
    return Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


@app.get("/healthz")
def healthz():
    REQUESTS.labels("/healthz").inc()
    return {"status": "alive"}, 200


@app.get("/readyz")
def readyz():
    REQUESTS.labels("/readyz").inc()
    try:
        with psycopg.connect(postgres_dsn(), connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        redis_client().ping()
    except Exception as exc:
        return {"status": "not-ready", "error": str(exc)}, 503
    return {"status": "ready"}, 200


@app.get("/api/info")
def info():
    REQUESTS.labels("/api/info").inc()
    config_path = Path(os.getenv("APP_CONFIG_FILE", "/app/config/app-config.yaml"))
    config = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    return jsonify(
        service="final-backend",
        version=os.getenv("APP_VERSION", "dev"),
        config=config,
    )


@app.post("/api/jobs")
def submit_job():
    REQUESTS.labels("/api/jobs").inc()
    payload = request.get_json(silent=True) or {"task": "demo"}
    redis_client().rpush("jobs", json.dumps(payload))
    return jsonify(status="queued", payload=payload), 202


@app.get("/api/jobs")
def jobs():
    REQUESTS.labels("/api/jobs:list").inc()
    with psycopg.connect(postgres_dsn()) as conn:
        rows = conn.execute(
            "SELECT id, payload, processed_at "
            "FROM processed_jobs ORDER BY id DESC LIMIT 20"
        ).fetchall()
    return jsonify(
        [
            {"id": row[0], "payload": row[1], "processed_at": row[2].isoformat()}
            for row in rows
        ]
    )


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": "text/plain; version=0.0.4"}
