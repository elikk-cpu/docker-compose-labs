import json
import os
import time

import pika
import psycopg


def postgres_dsn() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'database')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'jobs')} "
        f"user={os.getenv('POSTGRES_USER', 'jobs')} "
        f"password={os.getenv('POSTGRES_PASSWORD', '')}"
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


def connect_with_retry():
    while True:
        try:
            return pika.BlockingConnection(rabbit_parameters())
        except Exception as exc:
            print(f"rabbitmq not ready: {exc}", flush=True)
            time.sleep(2)


connection = connect_with_retry()
channel = connection.channel()
channel.queue_declare(queue="jobs", durable=True)


def handle(ch, method, _properties, body):
    payload = json.loads(body)
    with psycopg.connect(postgres_dsn()) as conn:
        conn.execute(
            "INSERT INTO processed_jobs(payload) VALUES (%s)",
            (json.dumps(payload),),
        )
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"processed: {payload}", flush=True)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="jobs", on_message_callback=handle)
print("worker waiting for jobs", flush=True)
channel.start_consuming()
