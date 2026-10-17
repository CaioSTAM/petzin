from fastapi import FastAPI
from fastapi.responses import JSONResponse
import psycopg

from app.donos import router as donos_router


app = FastAPI(title="PetzIn")
app.include_router(donos_router)


@app.exception_handler(psycopg.OperationalError)
def database_unavailable(request, exception):
    return JSONResponse(
        status_code=503,
        content={"detail": "Banco de dados indisponível. Tente novamente."},
    )


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
