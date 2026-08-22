from flask import Blueprint

ping_bp = Blueprint("ping", __name__)


@ping_bp.get("/ping")
def get_pong():
    return "pong", 200
