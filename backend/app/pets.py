from psycopg.errors import ForeignKeyViolation, RestrictViolation

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response

from app.database import get_connection
from app.schemas import IdPath, PetInput, PetResponse


router = APIRouter(prefix="/api/pets", tags=["Pets"])


def verificar_referencias(connection, dados: PetInput):
    dono = connection.execute("SELECT id FROM dono WHERE id=%s FOR KEY SHARE", (dados.dono_id,)).fetchone()
    if dono is None:
        raise HTTPException(status_code=404, detail="Dono não encontrado.")
    especie = connection.execute("SELECT id FROM especie WHERE id=%s FOR KEY SHARE", (dados.especie_id,)).fetchone()
    if especie is None:
        raise HTTPException(status_code=404, detail="Espécie não encontrada.")


@router.get("", response_model=list[PetResponse])
def listar_pets(dono_id: Annotated[int | None, Query(gt=0, le=2147483647)] = None):
    with get_connection() as connection:
        if dono_id is not None:
            return connection.execute(
                "SELECT id, nome, dono_id, especie_id, raca FROM pet WHERE dono_id=%s ORDER BY id", (dono_id,)
            ).fetchall()
        return connection.execute("SELECT id, nome, dono_id, especie_id, raca FROM pet ORDER BY id").fetchall()


@router.get("/{pet_id}", response_model=PetResponse)
def consultar_pet(pet_id: IdPath):
    with get_connection() as connection:
        pet = connection.execute("SELECT id, nome, dono_id, especie_id, raca FROM pet WHERE id=%s", (pet_id,)).fetchone()
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet não encontrado.")
    return pet


@router.post("", response_model=PetResponse, status_code=201)
def criar_pet(dados: PetInput):
    with get_connection() as connection:
        verificar_referencias(connection, dados)
        return connection.execute(
            "INSERT INTO pet (nome, dono_id, especie_id, raca) VALUES (%s, %s, %s, %s) RETURNING id, nome, dono_id, especie_id, raca",
            (dados.nome, dados.dono_id, dados.especie_id, dados.raca),
        ).fetchone()


@router.put("/{pet_id}", response_model=PetResponse)
def atualizar_pet(pet_id: IdPath, dados: PetInput):
    with get_connection() as connection:
        atual = connection.execute("SELECT dono_id, especie_id FROM pet WHERE id=%s FOR UPDATE", (pet_id,)).fetchone()
        if atual is None:
            raise HTTPException(status_code=404, detail="Pet não encontrado.")
        mudou_vinculo = atual["dono_id"] != dados.dono_id or atual["especie_id"] != dados.especie_id
        if mudou_vinculo:
            historico = connection.execute("SELECT 1 FROM reserva_pet WHERE pet_id=%s LIMIT 1", (pet_id,)).fetchone()
            if historico:
                raise HTTPException(status_code=409, detail="Pet com histórico não pode trocar de dono ou espécie.")
        verificar_referencias(connection, dados)
        return connection.execute(
            "UPDATE pet SET nome=%s, dono_id=%s, especie_id=%s, raca=%s WHERE id=%s RETURNING id, nome, dono_id, especie_id, raca",
            (dados.nome, dados.dono_id, dados.especie_id, dados.raca, pet_id),
        ).fetchone()


@router.delete("/{pet_id}", status_code=204)
def excluir_pet(pet_id: IdPath):
    try:
        with get_connection() as connection:
            pet = connection.execute("DELETE FROM pet WHERE id=%s RETURNING id", (pet_id,)).fetchone()
            if pet is None:
                raise HTTPException(status_code=404, detail="Pet não encontrado.")
    except (ForeignKeyViolation, RestrictViolation) as erro:
        raise HTTPException(status_code=409, detail="Este pet possui histórico de reservas e não pode ser excluído.") from erro
    return Response(status_code=204)
