from flask import Flask


def create_app():
    app = Flask(__name__)

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

    return app


app = create_app()
