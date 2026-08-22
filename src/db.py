import os

from sqlmodel import Session, create_engine, func, select

from .helpers import generate_short_link
from .models import Link, accepted_keys

database_url = os.environ["DATABASE_URL"]
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(database_url, echo=False)


def select_link(link_id: int | None = None, link_short_name: str | None = None):
    with Session(engine) as session:
        stmt = select(Link)

        if link_id is not None:
            stmt = stmt.where(Link.id == link_id)

        if link_short_name is not None:
            stmt = stmt.where(Link.short_name == link_short_name)
        return session.exec(stmt).one_or_none()


def select_links(
    offset: int = 0,
    limit: int = 10,
):
    with Session(engine) as session:
        stmt = select(Link).order_by(Link.id).offset(offset).limit(limit)

        return session.exec(stmt).all()


def insert_link(new_link: Link):
    with Session(engine) as session:
        session.add(new_link)
        session.commit()
        session.refresh(new_link)


def update_link(updated_link_id: int, payload):
    with Session(engine) as session:
        updated_link = session.get(Link, updated_link_id)

        if updated_link is None:
            return None

        for key, value in payload.items():
            if key in accepted_keys:
                setattr(updated_link, key, value)
        updated_link.short_url = generate_short_link(updated_link.short_name)

        session.commit()
        session.refresh(updated_link)

        return updated_link


def delete_link(deleted_link: Link):
    with Session(engine) as session:
        session.delete(deleted_link)
        session.commit()


def get_total_links():
    with Session(engine) as session:
        return session.exec(select(func.count()).select_from(Link)).one()
