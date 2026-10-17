import re
from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Texto = Annotated[str, Field(min_length=1)]
Identificador = Annotated[int, Field(gt=0, le=2147483647)]
IdPath = Annotated[int, Path(gt=0, le=2147483647)]


class Entrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def rejeitar_caractere_nulo(cls, value):
        if isinstance(value, str) and "\x00" in value:
            raise ValueError("Texto não pode conter caractere nulo.")
        return value


class DonoInput(Entrada):
    nome: Texto
    telefone: str

    @field_validator("telefone")
    @classmethod
    def telefone_internacional(cls, value):
        value = re.sub(r"[\s().-]", "", value)
        if not re.fullmatch(r"\+[1-9][0-9]{7,14}", value):
            raise ValueError("Use telefone internacional com +, código do país e 8 a 15 algarismos.")
        return value


class DonoResponse(BaseModel):
    id: int
    nome: str
    telefone: str


class PetInput(Entrada):
    nome: Texto
    dono_id: Identificador
    especie_id: Identificador
    raca: Texto | None = None

    @field_validator("raca", mode="before")
    @classmethod
    def raca_opcional(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value


class PetResponse(BaseModel):
    id: int
    nome: str
    dono_id: int
    especie_id: int
    raca: str | None


class EspecieInput(Entrada):
    nome: Texto


class EspecieResponse(BaseModel):
    id: int
    codigo: str
    nome: str


class CanilResponse(BaseModel):
    id: int


class Periodo(Entrada):
    data_entrada: date
    data_saida: date

    @model_validator(mode="after")
    def datas_em_ordem(self):
        if self.data_saida < self.data_entrada:
            raise ValueError("A saída deve ser igual ou posterior à entrada.")
        return self


class ReservaInput(Periodo):
    canil_id: Identificador
    pet_ids: Annotated[list[Identificador], Field(min_length=1, max_length=2)]

    @field_validator("pet_ids")
    @classmethod
    def pets_sem_repeticao(cls, value):
        if len(set(value)) != len(value):
            raise ValueError("Um pet não pode aparecer duas vezes na mesma reserva.")
        return value


class ReservaResponse(BaseModel):
    id: int
    canil_id: int
    data_entrada: date
    data_saida: date
    pet_ids: list[int]
    status: str
    tarifa_diaria: Decimal
    diarias: int
    valor_total: Decimal
