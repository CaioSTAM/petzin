from fastapi import APIRouter

from app.database import get_connection
from app.schemas import CanilResponse


router = APIRouter(prefix="/api/canis", tags=["Canis"])


@router.get("", response_model=list[CanilResponse])
def listar_canis():
    with get_connection() as connection:
        return connection.execute("SELECT id FROM canil ORDER BY id").fetchall()
