from src.db import select_link

from . import api_bp


@api_bp.get("/links/<int:link_id>")
def read_link_by_id(link_id: int):
    link = select_link(link_id)

    if link is None:
        return {"detail": "Not Found"}, 404

    return link.model_dump()
