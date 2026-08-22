from src.db import delete_link, select_link

from . import api_bp


@api_bp.delete("/links/<int:link_id>")
def delete_link_by_id(link_id: int):
    link = select_link(link_id=link_id)

    if link is None:
        return {"detail": "Not Found"}, 404

    delete_link(link)

    return "", 204
