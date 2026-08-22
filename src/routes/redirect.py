from flask import Blueprint, redirect

from src.db import select_link

redirect_bp = Blueprint("redirect", __name__, url_prefix="/r")


@redirect_bp.get("/<string:short_name>")
def redirect_by_short_name(short_name: str):
    link = select_link(link_short_name=short_name)

    if link is None:
        return {"detail": "Not Found"}, 404

    return redirect(link.original_url, 302)
