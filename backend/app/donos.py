from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel

from app.database import get_connection


router = APIRouter(prefix="/api/donos", tags=["Donos"])


class DonoResponse(BaseModel):
    id: int
    nome: str
    telefone: str


@router.get("", response_model=list[DonoResponse])
def listar_donos():
    with get_connection() as connection:
        return connection.execute("SELECT id, nome, telefone FROM dono ORDER BY id").fetchall()


@router.get("/{dono_id}", response_model=DonoResponse)
def consultar_dono(dono_id: Annotated[int, Path(gt=0)]):
    with get_connection() as connection:
        dono = connection.execute(
            "SELECT id, nome, telefone FROM dono WHERE id = %s", (dono_id,)
        ).fetchone()
    if dono is None:
        raise HTTPException(status_code=404, detail="Dono não encontrado.")
    return dono
