import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.main import app


def pet_payload(owner_id, **changes):
    return {"nome": "Rex", "dono_id": owner_id, "especie_id": 1, "raca": None} | changes


def saved_pet(client, owner_id):
    response = client.post("/api/pets", json=pet_payload(owner_id))
    assert response.status_code == 201
    return response.json()["id"]


def add_history(pet_id):
    with psycopg.connect(os.environ["DATABASE_URL"]) as connection:
        reservation_id = connection.execute(
            "INSERT INTO reserva (canil_id, data_entrada, data_saida) VALUES (1, '2026-10-20', '2026-10-22') RETURNING id"
        ).fetchone()[0]
        connection.execute("INSERT INTO reserva_pet VALUES (%s, %s)", (reservation_id, pet_id))


def test_owner_crud_normalizes_input(client, database):
    response = client.post("/api/donos", json={"nome": "  Outro tutor  ", "telefone": "+55 (92) 99999-9999"})
    assert response.status_code == 201
    owner = response.json()
    assert owner["nome"] == "Outro tutor"
    assert owner["telefone"] == "+5592999999999"
    assert client.get(f"/api/donos/{owner['id']}").json() == owner
    assert owner in client.get("/api/donos").json()
    updated = client.put(
        f"/api/donos/{owner['id']}",
        json={"nome": "Tutor atualizado", "telefone": "+5592888888888"},
    )
    assert updated.status_code == 200
    assert updated.json() == {"id": owner["id"], "nome": "Tutor atualizado", "telefone": "+5592888888888"}
    assert client.get(f"/api/donos/{owner['id']}").json() == updated.json()
    deleted = client.delete(f"/api/donos/{owner['id']}")
    assert deleted.status_code == 204 and deleted.content == b""
    assert client.get(f"/api/donos/{owner['id']}").status_code == 404


@pytest.mark.parametrize("body", [
    {"nome": "   ", "telefone": "+5592999999999"},
    {"nome": "Tutor", "telefone": "abc"},
])
def test_invalid_owner_input_is_rejected(client, database, body):
    assert client.post("/api/donos", json=body).status_code == 422


def test_delete_owner_with_pet_returns_409(client, database):
    saved_pet(client, database)
    assert client.delete(f"/api/donos/{database}").status_code == 409
    assert client.get(f"/api/donos/{database}").status_code == 200


def test_list_and_create_species(client, database):
    initial = client.get("/api/especies")
    assert initial.status_code == 200
    assert len(initial.json()) == 5
    response = client.post("/api/especies", json={"nome": "  Cágado  "})
    assert response.status_code == 201
    assert response.json()["nome"] == "Cágado"
    assert response.json()["codigo"] == "cagado"
    assert len(client.get("/api/especies").json()) == 6


def test_equivalent_species_returns_409(client, database):
    assert client.post("/api/especies", json={"nome": " COELHO "}).status_code == 409
    assert len(client.get("/api/especies").json()) == 5


def test_list_kennels_uses_only_identifier(client, database):
    response = client.get("/api/canis")
    assert response.status_code == 200
    assert response.json() == [{"id": identifier} for identifier in range(1, 16)]


def test_pet_crud_with_optional_breed(client, database):
    response = client.post("/api/pets", json=pet_payload(database, nome=" Rex ", raca="  "))
    assert response.status_code == 201
    pet = response.json()
    assert pet["nome"] == "Rex" and pet["raca"] is None
    pet_id = pet["id"]
    assert client.get(f"/api/pets/{pet_id}").json() == pet
    assert client.get(f"/api/pets?dono_id={database}").json() == [pet]
    updated = client.put(f"/api/pets/{pet_id}", json=pet_payload(database, nome="Rex atualizado", raca="Labrador"))
    assert updated.status_code == 200
    assert updated.json()["raca"] == "Labrador"
    assert client.delete(f"/api/pets/{pet_id}").status_code == 204
    assert client.get(f"/api/pets/{pet_id}").status_code == 404


@pytest.mark.parametrize("field", ["dono_id", "especie_id"])
def test_nonexistent_pet_reference_returns_404(client, database, field):
    response = client.post("/api/pets", json=pet_payload(database, **{field: 999999}))
    assert response.status_code == 404
    assert client.get("/api/pets").json() == []


def test_pet_with_history_cannot_be_deleted(client, database):
    pet_id = saved_pet(client, database)
    add_history(pet_id)
    assert client.delete(f"/api/pets/{pet_id}").status_code == 409
    assert client.get(f"/api/pets/{pet_id}").status_code == 200


@pytest.mark.parametrize("field", ["dono_id", "especie_id"])
def test_pet_with_history_cannot_change_relationship_but_can_correct_name(client, database, field):
    pet_id = saved_pet(client, database)
    add_history(pet_id)
    other = 2
    if field == "dono_id":
        response = client.post("/api/donos", json={"nome": "Outro tutor", "telefone": "+5592000000000"})
        assert response.status_code == 201
        other = response.json()["id"]
    assert client.put(f"/api/pets/{pet_id}", json=pet_payload(database, **{field: other})).status_code == 409
    corrected = client.put(f"/api/pets/{pet_id}", json=pet_payload(database, nome="Rex corrigido"))
    assert corrected.status_code == 200
    assert corrected.json()["especie_id"] == 1


def test_pet_without_history_can_change_species(client, database):
    pet_id = saved_pet(client, database)
    response = client.put(f"/api/pets/{pet_id}", json=pet_payload(database, especie_id=2))
    assert response.status_code == 200
    assert response.json()["especie_id"] == 2


def test_put_requires_complete_editable_owner_data(client, database):
    assert client.put(f"/api/donos/{database}", json={"nome": "Tutor"}).status_code == 422
    assert client.get(f"/api/donos/{database}").json()["nome"] == "Tutor de teste"


def test_null_character_in_text_returns_422(database):
    body = {"nome": "Texto\u0000inválido", "telefone": "+5592999999999"}
    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.post("/api/donos", json=body).status_code == 422
