from flask import request

from src.db import insert_link, select_link
from src.helpers import generate_short_link, push_error
from src.models import Link

from . import api_bp


def validate_payload(payload):
    errors = []

    if not isinstance(payload, dict):
        push_error(errors, ["body"], "Invalid payload")
        return errors

    for key in ["original_url", "short_name"]:
        if payload.get(key, "") == "":
            push_error(errors, ["body", key], f"{key} is empty")

    return errors


@api_bp.post("/links")
def create_link():
    payload = request.get_json(silent=True)
    validation_errors = validate_payload(payload)
    if len(validation_errors):
        return {"detail": validation_errors}, 422

    original_url = payload["original_url"]
    short_name = payload["short_name"]

    link = select_link(link_short_name=short_name)

    if link is not None:
        return {"detail": "Conflicted payload"}, 409

    new_link = Link(
        original_url=original_url,
        short_name=short_name,
        short_url=generate_short_link(short_name),
    )

    insert_link(new_link)

    return new_link.model_dump(), 201
