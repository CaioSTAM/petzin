from psycopg.errors import ForeignKeyViolation, RestrictViolation

from fastapi import APIRouter, HTTPException, Response

from app.database import get_connection
from app.schemas import DonoInput, DonoResponse, IdPath


router = APIRouter(prefix="/api/donos", tags=["Donos"])


@router.get("", response_model=list[DonoResponse])
def listar_donos():
    with get_connection() as connection:
        return connection.execute("SELECT id, nome, telefone FROM dono ORDER BY id").fetchall()


@router.get("/{dono_id}", response_model=DonoResponse)
def consultar_dono(dono_id: IdPath):
    with get_connection() as connection:
        dono = connection.execute(
            "SELECT id, nome, telefone FROM dono WHERE id = %s", (dono_id,)
        ).fetchone()
    if dono is None:
        raise HTTPException(status_code=404, detail="Dono não encontrado.")
    return dono


@router.post("", response_model=DonoResponse, status_code=201)
def criar_dono(dados: DonoInput):
    with get_connection() as connection:
        return connection.execute(
            "INSERT INTO dono (nome, telefone) VALUES (%s, %s) RETURNING id, nome, telefone",
            (dados.nome, dados.telefone),
        ).fetchone()


@router.put("/{dono_id}", response_model=DonoResponse)
def atualizar_dono(dono_id: IdPath, dados: DonoInput):
    with get_connection() as connection:
        dono = connection.execute(
            "UPDATE dono SET nome=%s, telefone=%s WHERE id=%s RETURNING id, nome, telefone",
            (dados.nome, dados.telefone, dono_id),
        ).fetchone()
        if dono is None:
            raise HTTPException(status_code=404, detail="Dono não encontrado.")
        return dono


@router.delete("/{dono_id}", status_code=204)
def excluir_dono(dono_id: IdPath):
    try:
        with get_connection() as connection:
            dono = connection.execute("DELETE FROM dono WHERE id=%s RETURNING id", (dono_id,)).fetchone()
            if dono is None:
                raise HTTPException(status_code=404, detail="Dono não encontrado.")
    except (ForeignKeyViolation, RestrictViolation) as erro:
        raise HTTPException(status_code=409, detail="Este dono possui pets cadastrados e não pode ser excluído.") from erro
    return Response(status_code=204)
