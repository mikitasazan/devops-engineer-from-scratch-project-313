import os

from flask import Flask
from flask_cors import CORS
from sqlmodel import SQLModel

from .db import engine
from .routes.api import api_bp
from .routes.ping import ping_bp
from .routes.redirect import redirect_bp


def create_app() -> Flask:
    app = Flask(__name__)

    if os.getenv("IS_DEVELOPMENT", "False") == "True":
        CORS(
            app,
            resources={
                r"/api/*": {
                    "origins": [
                        "http://127.0.0.1:5173",
                    ]
                }
            },
            supports_credentials=True,
            methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            expose_headers=["Content-Range"],
        )

    SQLModel.metadata.create_all(engine)

    app.register_blueprint(api_bp)
    app.register_blueprint(ping_bp)
    app.register_blueprint(redirect_bp)

    return app
