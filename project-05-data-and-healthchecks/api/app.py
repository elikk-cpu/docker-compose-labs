import json
import os
from contextlib import closing

import pika
import psycopg
from flask import Flask, jsonify, request
from redis import Redis

app = Flask(__name__)


def postgres_dsn() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'database')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'jobs')} "
        f"user={os.getenv('POSTGRES_USER', 'jobs')} "
        f"password={os.getenv('POSTGRES_PASSWORD', '')}"
    )


def redis_client() -> Redis:
    return Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def rabbit_parameters() -> pika.ConnectionParameters:
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "labuser"),
        os.getenv("RABBITMQ_PASS", ""),
    )
    return pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        virtual_host=os.getenv("RABBITMQ_VHOST", "/"),
        credentials=credentials,
    )


@app.get("/healthz")
def healthz():
    return {"status": "alive"}, 200


@app.get("/readyz")
def readyz():
    checks = {}
    try:
        with psycopg.connect(postgres_dsn(), connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        checks["postgres"] = "ok"
    except Exception as exc:
        checks["postgres"] = str(exc)

    try:
        redis_client().ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = str(exc)

    try:
        with closing(pika.BlockingConnection(rabbit_parameters())):
            checks["rabbitmq"] = "ok"
    except Exception as exc:
        checks["rabbitmq"] = str(exc)

    healthy = all(value == "ok" for value in checks.values())
    return jsonify(checks=checks), 200 if healthy else 503


@app.post("/jobs")
def create_job():
    payload = request.get_json(silent=True) or {}
    message = {"task": payload.get("task", "demo")}

    connection = pika.BlockingConnection(rabbit_parameters())
    try:
        channel = connection.channel()
        channel.queue_declare(queue="jobs", durable=True)
        channel.basic_publish(
            exchange="",
            routing_key="jobs",
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        connection.close()

    redis_client().incr("jobs_submitted")
    return jsonify(status="queued", message=message), 202


@app.get("/stats")
def stats():
    with psycopg.connect(postgres_dsn()) as conn:
        processed = conn.execute("SELECT count(*) FROM processed_jobs").fetchone()[0]
    submitted = int(redis_client().get("jobs_submitted") or 0)
    return jsonify(submitted=submitted, processed=processed)
