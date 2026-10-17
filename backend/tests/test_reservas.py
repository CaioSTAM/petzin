from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import reservas


def pet(client, owner, species=1):
    response = client.post("/api/pets", json={"nome": "Pet de teste", "dono_id": owner, "especie_id": species})
    assert response.status_code == 201
    return response.json()["id"]


def booking(pets, **changes):
    return {"canil_id": 1, "pet_ids": pets, "data_entrada": "2026-10-20", "data_saida": "2026-10-22"} | changes


def test_reservation_lifecycle_preserves_rate_and_history(client, database, monkeypatch):
    pets = [pet(client, database), pet(client, database)]
    created = client.post("/api/reservas", json=booking(pets))
    assert created.status_code == 201
    reservation = created.json()
    assert reservation["pet_ids"] == pets
    assert reservation["diarias"] == 3
    assert reservation["tarifa_diaria"] == "50.00"
    assert reservation["valor_total"] == "150.00"
    identifier = reservation["id"]
    assert client.get(f"/api/reservas/{identifier}").json() == reservation
    assert reservation in client.get("/api/reservas").json()
    monkeypatch.setattr(reservas, "TARIFA_DIARIA", Decimal("60.00"))
    updated = client.put(f"/api/reservas/{identifier}", json=booking(pets, data_saida="2026-10-20"))
    assert updated.status_code == 200
    assert updated.json()["diarias"] == 1
    assert updated.json()["valor_total"] == "50.00"
    assert updated.json()["tarifa_diaria"] == reservation["tarifa_diaria"]
    assert client.delete(f"/api/reservas/{identifier}").status_code == 204
    assert client.get(f"/api/reservas/{identifier}").json()["status"] == "cancelada"
    assert client.delete(f"/api/pets/{pets[0]}").status_code == 409
    assert client.put(f"/api/reservas/{identifier}", json=booking(pets)).status_code == 409
    new = client.post("/api/reservas", json=booking(pets))
    assert new.status_code == 201
    assert new.json()["valor_total"] == "180.00"


def test_availability_respects_inclusive_dates_and_cancellation(client, database):
    response = client.post("/api/reservas", json=booking([pet(client, database)]))
    assert response.status_code == 201
    def available(start):
        result = client.get("/api/canis/disponiveis", params={"data_entrada": start, "data_saida": "2026-10-24"})
        assert result.status_code == 200
        return [item["id"] for item in result.json()]
    assert available("2026-10-22") == list(range(2, 16))
    assert available("2026-10-23") == list(range(1, 16))
    assert client.delete(f"/api/reservas/{response.json()['id']}").status_code == 204
    assert available("2026-10-22") == list(range(1, 16))


@pytest.mark.parametrize("case", ["tres_pets", "gatos", "donos_diferentes"])
def test_invalid_sharing_leaves_no_reservation(client, database, case):
    owner = database
    if case == "donos_diferentes":
        owner = client.post("/api/donos", json={"nome": "Outro", "telefone": "+5592000000000"}).json()["id"]
    species = 2 if case == "gatos" else 1
    pets = [pet(client, database, species), pet(client, owner, species)]
    if case == "tres_pets":
        pets.append(pet(client, database))
    assert client.post("/api/reservas", json=booking(pets)).status_code == 422
    assert client.get("/api/reservas").json() == []


def test_conflicting_edit_is_rolled_back(client, database):
    first = client.post("/api/reservas", json=booking([pet(client, database)]))
    second = client.post("/api/reservas", json=booking([pet(client, database)], canil_id=2))
    assert first.status_code == second.status_code == 201
    identifier = second.json()["id"]
    assert client.put(f"/api/reservas/{identifier}", json=booking(second.json()["pet_ids"])).status_code == 409
    assert client.get(f"/api/reservas/{identifier}").json() == second.json()


@pytest.mark.parametrize("change", [{"data_saida": "2026-10-19"}, {"pet_ids": []}, {"pet_ids": [1, 1]}])
def test_invalid_booking_input(client, database, change):
    assert client.post("/api/reservas", json=booking([pet(client, database)], **change)).status_code == 422


def test_missing_references_and_reservation_return_404(client, database):
    assert client.post("/api/reservas", json=booking([999999])).status_code == 404
    assert client.post("/api/reservas", json=booking([pet(client, database)], canil_id=999)).status_code == 404
    missing = client.get("/api/reservas/999999")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Reserva não encontrada."


@pytest.mark.parametrize("same_pet", [False, True])
def test_simultaneous_bookings_cannot_share_kennel_or_pet(client, database, same_pet):
    first = pet(client, database)
    second = first if same_pet else pet(client, database)
    requests = [booking([first]), booking([second], canil_id=2 if same_pet else 1)]
    barrier = Barrier(2)
    def submit(body):
        with TestClient(app) as session:
            barrier.wait(timeout=10)
            return session.post("/api/reservas", json=body).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(submit, requests))
    assert sorted(statuses) == [201, 409]
    assert len(client.get("/api/reservas").json()) == 1
