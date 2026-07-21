import os

from flask import Flask, jsonify
from redis import Redis

app = Flask(__name__)
redis_client = Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.get("/api/counter")
def counter():
    value = redis_client.incr("requests")
    return jsonify(counter=value)
