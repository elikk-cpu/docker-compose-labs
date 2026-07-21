from flask import Flask

app = Flask(__name__)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200
