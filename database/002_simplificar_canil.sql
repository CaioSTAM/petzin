-- Somente para bancos que já receberam a estrutura anterior de Canil.
-- Aplicar com --single-transaction e ON_ERROR_STOP=1.
-- Não renumera IDs nem modifica as referências de Reserva.

LOCK TABLE canil IN ACCESS EXCLUSIVE MODE;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'canil' AND column_name = 'numero'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM canil
            WHERE id <> numero OR id NOT BETWEEN 1 AND 15
        ) THEN
            RAISE EXCEPTION 'Canis com ID e número divergentes: revisar antes de simplificar';
        END IF;

        ALTER TABLE canil DROP COLUMN numero;
    END IF;

    ALTER TABLE canil ALTER COLUMN id DROP IDENTITY IF EXISTS;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'canil'::regclass AND conname = 'canil_id_faixa'
    ) THEN
        ALTER TABLE canil ADD CONSTRAINT canil_id_faixa
            CHECK (id BETWEEN 1 AND 15);
    END IF;
END;
$$;
