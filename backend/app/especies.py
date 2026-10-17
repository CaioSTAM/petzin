import re
import unicodedata

from fastapi import APIRouter, HTTPException

from app.database import get_connection
from app.schemas import EspecieInput, EspecieResponse


router = APIRouter(prefix="/api/especies", tags=["Espécies"])


@router.get("", response_model=list[EspecieResponse])
def listar_especies():
    with get_connection() as connection:
        return connection.execute("SELECT id, codigo, nome FROM especie ORDER BY nome").fetchall()


@router.post("", response_model=EspecieResponse, status_code=201)
def criar_especie(dados: EspecieInput):
    sem_acentos = unicodedata.normalize("NFKD", dados.nome).encode("ascii", "ignore").decode()
    codigo = re.sub(r"[^a-z0-9]+", "_", sem_acentos.lower()).strip("_")
    if not codigo or not codigo[0].isalpha():
        raise HTTPException(status_code=422, detail="Informe um nome de espécie iniciado por uma letra.")
    with get_connection() as connection:
        return connection.execute(
            "INSERT INTO especie (codigo, nome) VALUES (%s, %s) RETURNING id, codigo, nome",
            (codigo, dados.nome),
        ).fetchone()
