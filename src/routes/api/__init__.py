from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from . import (  # noqa: E402
    create_link,
    delete_link_by_id,
    read_link_by_id,
    read_links,
    update_link_by_id,
)
