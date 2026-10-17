from decimal import Decimal

from fastapi import APIRouter, HTTPException, Response

from app.database import get_connection
from app.schemas import IdPath, ReservaInput, ReservaResponse


router = APIRouter(prefix="/api/reservas", tags=["Reservas"])
TARIFA_DIARIA = Decimal("50.00")
CONSULTA = """
    SELECT r.*, ARRAY(SELECT pet_id FROM reserva_pet WHERE reserva_id=r.id ORDER BY pet_id) AS pet_ids
    FROM reserva r
"""


def resposta(reserva):
    reserva["diarias"] = (reserva["data_saida"] - reserva["data_entrada"]).days + 1
    reserva["valor_total"] = reserva["tarifa_diaria"] * reserva["diarias"]
    return reserva


def buscar(connection, reserva_id, bloquear=False):
    consulta = CONSULTA + " WHERE r.id=%s" + (" FOR UPDATE OF r" if bloquear else "")
    reserva = connection.execute(consulta, (reserva_id,)).fetchone()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")
    return reserva


def bloquear_canis(connection, canil_id, canil_anterior=None):
    canil_ids = sorted({canil_id} | ({canil_anterior} if canil_anterior is not None else set()))
    # Serializa gravações do mesmo canil antes da verificação de ocupação.
    # O bloqueio também evita impasses entre inserções na restrição de exclusão.
    canis = connection.execute(
        "SELECT id FROM canil WHERE id=ANY(%s) ORDER BY id FOR NO KEY UPDATE", (canil_ids,),
    ).fetchall()
    if not any(canil["id"] == canil_id for canil in canis):
        raise HTTPException(status_code=404, detail="Canil não encontrado.")


def bloquear_pets(connection, pet_ids, pets_anteriores=()):
    # Uma ordem fixa evita que duas alterações bloqueiem os mesmos pets em ordem inversa.
    ids_para_bloquear = sorted(set(pet_ids) | set(pets_anteriores))
    pets = connection.execute(
        """SELECT p.id, p.dono_id, e.codigo FROM pet p JOIN especie e ON e.id=p.especie_id
           WHERE p.id = ANY(%s) ORDER BY p.id FOR UPDATE OF p""", (ids_para_bloquear,),
    ).fetchall()
    return pets


def validar_participantes(pets, pet_ids):
    pets_selecionados = [pet for pet in pets if pet["id"] in pet_ids]
    if len(pets_selecionados) != len(pet_ids):
        raise HTTPException(status_code=404, detail="Pet não encontrado.")
    if len(pets_selecionados) == 2 and (
        any(pet["codigo"] != "cachorro" for pet in pets_selecionados)
        or pets_selecionados[0]["dono_id"] != pets_selecionados[1]["dono_id"]
    ):
        raise HTTPException(status_code=422, detail="Somente dois cachorros do mesmo dono podem compartilhar um canil.")


def verificar_conflitos(connection, dados, reserva_id):
    # Esta consulta ocorre depois dos bloqueios: enxerga a confirmação de uma gravação concorrente.
    conflito = connection.execute(
        """SELECT 1 FROM reserva r
           WHERE r.status='ativa' AND r.id<>%s
             AND r.data_entrada<=%s AND r.data_saida>=%s
             AND (r.canil_id=%s OR EXISTS (
                 SELECT 1 FROM reserva_pet rp WHERE rp.reserva_id=r.id AND rp.pet_id=ANY(%s)))
           LIMIT 1""",
        (reserva_id, dados.data_saida, dados.data_entrada, dados.canil_id, dados.pet_ids),
    ).fetchone()
    if conflito:
        raise HTTPException(status_code=409, detail="Canil ou pet já reservado nesse período.")


def preparar_gravacao_reserva(
    connection, dados, reserva_id=0, pets_anteriores=(), canil_anterior=None,
):
    # Todos os passos usam a mesma conexão e transação do endpoint.
    bloquear_canis(connection, dados.canil_id, canil_anterior)
    pets = bloquear_pets(connection, dados.pet_ids, pets_anteriores)
    validar_participantes(pets, dados.pet_ids)
    verificar_conflitos(connection, dados, reserva_id)


def vincular_pets(connection, reserva_id, pet_ids):
    for pet_id in sorted(pet_ids):
        connection.execute("INSERT INTO reserva_pet (reserva_id, pet_id) VALUES (%s, %s)", (reserva_id, pet_id))


@router.get("", response_model=list[ReservaResponse])
def listar_reservas():
    with get_connection() as connection:
        return [resposta(reserva) for reserva in connection.execute(CONSULTA + " ORDER BY r.id").fetchall()]


@router.get("/{reserva_id}", response_model=ReservaResponse)
def consultar_reserva(reserva_id: IdPath):
    with get_connection() as connection:
        return resposta(buscar(connection, reserva_id))


@router.post("", response_model=ReservaResponse, status_code=201)
def criar_reserva(dados: ReservaInput):
    with get_connection() as connection:
        preparar_gravacao_reserva(connection, dados)
        reserva_id = connection.execute(
            """INSERT INTO reserva (canil_id, data_entrada, data_saida, tarifa_diaria)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (dados.canil_id, dados.data_entrada, dados.data_saida, TARIFA_DIARIA),
        ).fetchone()["id"]
        vincular_pets(connection, reserva_id, dados.pet_ids)
        return resposta(buscar(connection, reserva_id))


@router.put("/{reserva_id}", response_model=ReservaResponse)
def atualizar_reserva(reserva_id: IdPath, dados: ReservaInput):
    with get_connection() as connection:
        reserva_atual = buscar(connection, reserva_id, bloquear=True)
        if reserva_atual["status"] == "cancelada":
            raise HTTPException(status_code=409, detail="Reserva cancelada não pode ser alterada.")
        preparar_gravacao_reserva(
            connection, dados, reserva_id, reserva_atual["pet_ids"], reserva_atual["canil_id"],
        )
        connection.execute(
            "UPDATE reserva SET canil_id=%s, data_entrada=%s, data_saida=%s WHERE id=%s",
            (dados.canil_id, dados.data_entrada, dados.data_saida, reserva_id),
        )
        connection.execute("DELETE FROM reserva_pet WHERE reserva_id=%s", (reserva_id,))
        vincular_pets(connection, reserva_id, dados.pet_ids)
        return resposta(buscar(connection, reserva_id))


@router.delete("/{reserva_id}", status_code=204)
def cancelar_reserva(reserva_id: IdPath):
    with get_connection() as connection:
        buscar(connection, reserva_id, bloquear=True)
        connection.execute("UPDATE reserva SET status='cancelada' WHERE id=%s", (reserva_id,))
    return Response(status_code=204)
