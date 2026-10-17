from fastapi import FastAPI
from fastapi.responses import JSONResponse
import psycopg

from app.donos import router as donos_router
from app.pets import router as pets_router
from app.especies import router as especies_router
from app.canis import router as canis_router
from app.reservas import router as reservas_router


app = FastAPI(title="PetzIn")
app.include_router(donos_router)
app.include_router(pets_router)
app.include_router(especies_router)
app.include_router(canis_router)
app.include_router(reservas_router)


@app.exception_handler(psycopg.IntegrityError)
def integrity_conflict(request, exception):
    if isinstance(exception, psycopg.errors.ExclusionViolation):
        detail = "Canil já reservado nesse período."
    elif isinstance(exception, psycopg.errors.UniqueViolation):
        detail = "Já existe um cadastro com esse nome ou código equivalente."
    elif isinstance(exception, (psycopg.errors.ForeignKeyViolation, psycopg.errors.RestrictViolation)):
        detail = "Operação não permitida: o cadastro possui vínculos ou a referência não existe."
    else:
        detail = "A operação viola uma regra de integridade dos dados."
    return JSONResponse(status_code=409, content={"detail": detail})


@app.exception_handler(psycopg.OperationalError)
def database_unavailable(request, exception):
    return JSONResponse(
        status_code=503,
        content={"detail": "Banco de dados indisponível. Tente novamente."},
    )


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
