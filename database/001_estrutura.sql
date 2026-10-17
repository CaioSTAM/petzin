-- Aplicar com psql --single-transaction e ON_ERROR_STOP=1.
-- Não altera os dados do cadastro de dono já criado durante a mentoria.

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;

CREATE TABLE IF NOT EXISTS dono (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL CHECK (btrim(nome) <> ''),
    telefone TEXT NOT NULL CHECK (btrim(telefone) <> '')
);

CREATE TABLE IF NOT EXISTS especie (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE CHECK (codigo ~ '^[a-z][a-z0-9_]*$'),
    nome TEXT NOT NULL CHECK (btrim(nome) <> '')
);

-- Unicidade de grafia equivalente; não identifica sinônimos.
CREATE UNIQUE INDEX IF NOT EXISTS especie_nome_normalizado_unico
    ON especie (lower(btrim(nome)));

CREATE TABLE IF NOT EXISTS pet (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL CHECK (btrim(nome) <> ''),
    dono_id INTEGER NOT NULL REFERENCES dono(id) ON DELETE RESTRICT,
    especie_id INTEGER NOT NULL REFERENCES especie(id) ON DELETE RESTRICT,
    raca TEXT CHECK (raca IS NULL OR btrim(raca) <> '')
);

CREATE INDEX IF NOT EXISTS pet_dono_idx ON pet(dono_id);
CREATE INDEX IF NOT EXISTS pet_especie_idx ON pet(especie_id);

CREATE TABLE IF NOT EXISTS canil (
    id INTEGER PRIMARY KEY,
    CONSTRAINT canil_id_faixa CHECK (id BETWEEN 1 AND 15)
);

CREATE TABLE IF NOT EXISTS reserva (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    canil_id INTEGER NOT NULL REFERENCES canil(id) ON DELETE RESTRICT,
    data_entrada DATE NOT NULL CHECK (isfinite(data_entrada)),
    data_saida DATE NOT NULL CHECK (isfinite(data_saida)),
    tarifa_diaria NUMERIC(10,2) NOT NULL DEFAULT 50.00
        CHECK (tarifa_diaria > 0 AND tarifa_diaria <> 'NaN'::numeric),
    status TEXT NOT NULL DEFAULT 'ativa' CHECK (status IN ('ativa', 'cancelada')),
    CONSTRAINT reserva_datas_validas CHECK (data_saida >= data_entrada),
    -- [] inclui entrada e saída: outra reserva começa somente no dia seguinte.
    CONSTRAINT reserva_canil_sem_sobreposicao
        EXCLUDE USING gist (
            canil_id public.gist_int4_ops WITH =,
            daterange(data_entrada, data_saida, '[]') WITH &&
        ) WHERE (status = 'ativa')
);

CREATE TABLE IF NOT EXISTS reserva_pet (
    reserva_id INTEGER NOT NULL REFERENCES reserva(id) ON DELETE CASCADE,
    pet_id INTEGER NOT NULL REFERENCES pet(id) ON DELETE RESTRICT,
    PRIMARY KEY (reserva_id, pet_id)
);

CREATE INDEX IF NOT EXISTS reserva_pet_pet_idx ON reserva_pet(pet_id);

-- Códigos ficam estáveis mesmo que um nome de exibição seja corrigido.
INSERT INTO especie (codigo, nome) VALUES
    ('cachorro', 'Cachorro'),
    ('gato', 'Gato'),
    ('coelho', 'Coelho'),
    ('hamster', 'Hamster'),
    ('porquinho_da_india', 'Porquinho-da-índia')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO canil (id)
SELECT generate_series(1, 15)
ON CONFLICT (id) DO NOTHING;
