import importlib

import pytest
from sqlmodel import Session, SQLModel, create_engine, select


@pytest.fixture()
def test_engine(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    test_db_url = f"sqlite:///{db_file}"

    monkeypatch.setenv("DATABASE_URL", test_db_url)
    monkeypatch.setenv("BASE_URL", "short.local")

    db_module = importlib.import_module("src.db")
    app_module = importlib.import_module("src.app")
    routes_module = importlib.import_module("src.routes")

    test_engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    monkeypatch.setattr(db_module, "engine", test_engine, raising=False)
    monkeypatch.setattr(app_module, "engine", test_engine, raising=False)
    monkeypatch.setattr(routes_module, "engine", test_engine, raising=False)

    app_module.create_app()
    yield test_engine

    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture()
def app(test_engine):
    app_module = importlib.import_module("src.app")
    app = app_module.create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def _seed_link(engine, suffix: str):
    from src.models import Link

    with Session(engine) as session:
        link = Link(
            original_url=f"https://example.com/{suffix}",
            short_name=f"name-{suffix}",
            short_url=f"https://short.local/name-{suffix}/abc123",
        )
        session.add(link)
        session.commit()
        session.refresh(link)

        return link.id


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "pong"


def test_read_links(client, test_engine):

    _seed_link(test_engine, "one")
    _seed_link(test_engine, "two")
    _seed_link(test_engine, "three")
    _seed_link(test_engine, "four")

    # Happy path - 200
    response = client.get("/api/links")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 4

    # Happy path with range - 200
    response = client.get("/api/links?range=[1,5]")
    assert response.status_code == 200
    assert response.headers["Content-Range"] == "links 1-5/4"

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 3

    # Range validation errors - 400
    response = client.get("/api/links?range=[5]")
    assert response.status_code == 400

    response = client.get("/api/links?range=[5, 1]")
    assert response.status_code == 400

    response = client.get("/api/links?range=['a' 1]")
    assert response.status_code == 400

    response = client.get("/api/links?range=[]")
    assert response.status_code == 400

    response = client.get("/api/links?range=[-1, 1]")
    assert response.status_code == 400


def test_create_link(client):
    # Happy path - 201
    payload = {
        "original_url": "https://example.com/new",
        "short_name": "new-link",
    }
    response = client.post("/api/links", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["original_url"] == payload["original_url"]
    assert data["short_name"] == payload["short_name"]
    assert data["id"] is not None
    assert "short_url" in data

    # Попытка создать новую сущность с тем же short_name - 409
    response = client.post("/api/links", json=payload)
    assert response.status_code == 409

    # Попытка создать новую сущность с пустым payload - 422
    response = client.post("/api/links", json={})
    assert response.status_code == 422

    # Попытка создать новую сущность с частично пустым payload - 422
    response = client.post(
        "/api/links", json={"original_url": "https://example.com/only-url"}
    )
    assert response.status_code == 422

    response = client.post("/api/links", json={"short_name": "only-name"})
    assert response.status_code == 422


def test_read_link_by_id(client, test_engine):
    link_id = _seed_link(test_engine, "read")

    # Happy path - 204
    response = client.get(f"/api/links/{link_id}")
    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == link_id
    assert data["short_name"] == "name-read"

    # Сущность не найдена - 404
    response = client.get(f"/api/links/{link_id + 1}")
    assert response.status_code == 404


def test_update_link_by_id(client, test_engine):
    # Happy path - 200
    link_id = _seed_link(test_engine, "update-old")
    another_link_id = _seed_link(test_engine, "other-update-old")
    payload = {
        "original_url": "https://example.com/update-new",
        "short_name": "name-update-new",
    }

    response = client.put(f"/api/links/{link_id}", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    short_url = data["short_url"]

    # Идемпотентность - 200
    response = client.put(f"/api/links/{link_id}", json=payload)
    assert response.status_code == 200

    # Обновление сущности только одним поле из двух - 200
    partial_payload = {"original_url": "https://example.com/update-only-url"}
    response = client.put(f"/api/links/{link_id}", json=partial_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["original_url"] == partial_payload["original_url"]
    assert data["short_name"] == payload["short_name"]
    assert data["short_url"] == short_url

    # Обновление сущности на существующее имя - 409
    payload_with_same_name = {
        "short_name": payload["short_name"],
    }
    response = client.put(
        f"/api/links/{another_link_id}", json=payload_with_same_name
    )
    assert response.status_code == 409

    # Сущность для апдейта не найдена - 404
    response = client.put(f"/api/links/{link_id + 2}", json=payload)
    assert response.status_code == 404

    # Ошибки валидатора - 422
    response = client.put(f"/api/links/{link_id}", json=None)
    assert response.status_code == 422

    payload_with_wrong_type = {
        "short_name": 4.12,
    }
    response = client.put(
        f"/api/links/{link_id}",
        json=payload_with_wrong_type,
    )
    assert response.status_code == 422


def test_delete_link_by_id(client, test_engine):
    from src.models import Link

    # Happy path - 204
    link_id = _seed_link(test_engine, "delete")
    response = client.delete(f"/api/links/{link_id}")
    assert response.status_code == 204

    with Session(test_engine) as session:
        deleted = session.exec(
            select(Link).where(Link.id == link_id)
        ).one_or_none()
        assert deleted is None

    # Отказ от идемпотентности удаления - 404
    response = client.delete(f"/api/links/{link_id}")
    assert response.status_code == 404

    # Сущность для удаления не найдена - 404
    response = client.delete(f"/api/links/{link_id + 1}")
    assert response.status_code == 404


def test_redirect(client, test_engine):
    # Happy path -  302
    _seed_link(test_engine, "super-url")

    response = client.get("/r/name-super-url")
    assert response.status_code == 302
    assert response.headers["Location"] == "https://example.com/super-url"

    # Сущность не найдена, короткой ссылки нет - 404
    response = client.get("/r/name-non-super-url")
    assert response.status_code == 404
