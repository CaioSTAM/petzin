from typing import Annotated

from fastapi import APIRouter, Query

from app.database import get_connection
from app.schemas import CanilResponse, Periodo


router = APIRouter(prefix="/api/canis", tags=["Canis"])


@router.get("", response_model=list[CanilResponse])
def listar_canis():
    with get_connection() as connection:
        return connection.execute("SELECT id FROM canil ORDER BY id").fetchall()


@router.get("/disponiveis", response_model=list[CanilResponse])
def listar_canis_disponiveis(periodo: Annotated[Periodo, Query()]):
    with get_connection() as connection:
        return connection.execute(
            """SELECT c.id FROM canil c WHERE NOT EXISTS (
                 SELECT 1 FROM reserva r WHERE r.canil_id=c.id AND r.status='ativa'
                 AND r.data_entrada<=%s AND r.data_saida>=%s
               ) ORDER BY c.id""", (periodo.data_saida, periodo.data_entrada),
        ).fetchall()
