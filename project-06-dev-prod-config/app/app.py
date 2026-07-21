import os
from pathlib import Path

import yaml
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.get("/config")
def config():
    path = Path(os.getenv("APP_CONFIG_FILE", "/app/config/app-config.yaml"))
    file_config = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    return jsonify(
        environment=os.getenv("APP_ENV", "unknown"),
        log_level=os.getenv("LOG_LEVEL", "info"),
        file_config=file_config,
    )
