import pytest


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database(client, database):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_missing_owner_returns_404(client, database):
    response = client.get("/api/donos/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Dono não encontrado."}


@pytest.mark.parametrize("identifier", ["0", "texto"])
def test_invalid_id_returns_422(client, identifier, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "host=127.0.0.1 port=1 dbname=petzin user=postgres connect_timeout=1")
    assert client.get(f"/api/donos/{identifier}").status_code == 422


def test_unavailable_database_returns_controlled_error(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "host=127.0.0.1 port=1 dbname=petzin user=postgres connect_timeout=1")
    response = client.get("/api/donos")
    assert response.status_code == 503
    assert response.json() == {"detail": "Banco de dados indisponível. Tente novamente."}
    assert client.get("/health").status_code == 200
    readiness = client.get("/ready")
    assert readiness.status_code == 503
    assert readiness.json() == response.json()
