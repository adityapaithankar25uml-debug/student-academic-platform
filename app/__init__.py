from flask import Flask

from database.db import initialize_database
from app.routes import api


def create_app():
    app = Flask(__name__)

    initialize_database()

    @app.get("/")
    def home():
        return {
            "application": "Student Academic Management Platform",
            "status": "running"
        }

    @app.get("/health")
    def health():
        return {
            "status": "healthy"
        }

    app.register_blueprint(api, url_prefix="/api")

    return app


app = create_app()
