from flask import request

from src.db import select_link, update_link
from src.helpers import (
    push_error,
)
from src.models import accepted_keys

from . import api_bp


def validate_payload(payload):
    errors = []

    if not isinstance(payload, dict):
        push_error(errors, ["body"], "Invalid payload")
        return errors

    if payload == {}:
        push_error(errors, ["body"], "Payload is empty")
        return errors

    for key in accepted_keys:
        key_value = payload.get(key)
        if key_value is None:
            continue

        if not isinstance(key_value, str):
            push_error(errors, ["body", key], f"{key} is not string")

    return errors


@api_bp.put("/links/<int:link_id>")
def update_link_by_id(link_id: int):
    payload = request.get_json(silent=True)
    validation_errors = validate_payload(payload)
    if len(validation_errors):
        return {"detail": validation_errors}, 422

    link = select_link(link_id=link_id)

    if link is None:
        return {"detail": "Not Found"}, 404

    short_name = payload.get("short_name", None)
    if short_name:
        another_link = select_link(link_short_name=short_name)
        if another_link is not None and another_link.id != link.id:
            return {"detail": "Conflicted payload"}, 409

    updated_link = update_link(link.id, payload)

    return updated_link.model_dump(), 200
