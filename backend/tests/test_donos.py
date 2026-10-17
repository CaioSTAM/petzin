import os
from pathlib import Path
import uuid

from fastapi.testclient import TestClient
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
import pytest

from app.main import app


ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATABASE = "host=localhost port=5432 dbname=petzin user=postgres connect_timeout=5"


@pytest.fixture
def database(monkeypatch):
    base = os.getenv("DATABASE_URL", LOCAL_DATABASE)
    schema = "petzin_api_test_" + uuid.uuid4().hex
    with psycopg.connect(base, autocommit=True) as admin:
        try:
            with admin.transaction():
                admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
                admin.execute(sql.SQL("SET LOCAL search_path TO {}").format(sql.Identifier(schema)))
                admin.execute((ROOT / "database/001_estrutura.sql").read_text(encoding="utf-8"))
                owner_id = admin.execute(
                    "INSERT INTO dono (nome, telefone) VALUES (%s, %s) RETURNING id",
                    ("Tutor de teste", "+5592000000000"),
                ).fetchone()[0]
            monkeypatch.setenv("DATABASE_URL", make_conninfo(base, options=f"-c search_path={schema}"))
            yield owner_id
        finally:
            admin.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))


@pytest.fixture
def client():
    with TestClient(app) as instance:
        yield instance


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_owners_reads_isolated_database(client, database):
    response = client.get("/api/donos")
    assert response.status_code == 200
    assert response.json() == [{"id": database, "nome": "Tutor de teste", "telefone": "+5592000000000"}]


def test_get_owner_by_id(client, database):
    response = client.get(f"/api/donos/{database}")
    assert response.status_code == 200
    assert response.json() == {"id": database, "nome": "Tutor de teste", "telefone": "+5592000000000"}


def test_missing_owner_returns_404(client, database):
    response = client.get("/api/donos/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Dono não encontrado."}


@pytest.mark.parametrize("identifier", ["0", "-1", "texto"])
def test_invalid_id_returns_422(client, identifier, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "host=127.0.0.1 port=1 dbname=petzin user=postgres connect_timeout=1")
    assert client.get(f"/api/donos/{identifier}").status_code == 422


def test_unavailable_database_returns_controlled_error(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "host=127.0.0.1 port=1 dbname=petzin user=postgres connect_timeout=1")
    response = client.get("/api/donos")
    assert response.status_code == 503
    assert response.json() == {"detail": "Banco de dados indisponível. Tente novamente."}
