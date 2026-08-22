import json

from flask import jsonify, make_response, request

from src.db import get_total_links, select_links

from . import api_bp


@api_bp.get("/links")
def read_links():
    raw_range = request.args.get("range", "[0, 9]")
    try:
        range_list = json.loads(raw_range)
        if (
            not len(range_list) == 2
            or not all(isinstance(value, int) for value in range_list)
            or range_list[0] > range_list[1]
            or range_list[0] < 0
        ):
            raise ValueError
    except json.JSONDecodeError, TypeError, ValueError:
        return jsonify({"detail": "Bad request"}), 400

    min = int(range_list[0])
    max = int(range_list[1])

    results = select_links(offset=min, limit=max + 1 - min)
    total = get_total_links()

    response = make_response(
        jsonify([link.model_dump() for link in results]), 200
    )
    response.headers["Content-Range"] = f"links {min}-{max}/{total}"

    return response
