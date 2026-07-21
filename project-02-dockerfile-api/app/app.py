import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.get("/api/info")
def info():
    return jsonify(
        service="dockerfile-api",
        version=os.getenv("APP_VERSION", "dev"),
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=os.getenv("APP_PORT", "5000"),
    )


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host=host, port=port)
