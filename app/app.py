import os
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(
        service="hello-flask",
        version=os.getenv("APP_VERSION", "dev"),
        environment=os.getenv("APP_ENV", "local"),
    )


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")
