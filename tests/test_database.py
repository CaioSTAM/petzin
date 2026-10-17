"""Testes do contrato do banco; cada caso cria um schema e reverte tudo."""

import os
from pathlib import Path
import shutil
import subprocess
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database" / "001_estrutura.sql"
SIMPLIFICATION = ROOT / "database" / "002_simplificar_canil.sql"
PSQL = os.environ.get("PSQL_PATH") or shutil.which("psql")
if not PSQL:
    candidate = Path(r"C:\Program Files\PostgreSQL\18\bin\psql.exe")
    PSQL = str(candidate) if candidate.is_file() else "psql"


class DatabaseTests(unittest.TestCase):
    def execute(self, statement, ddl=None):
        schema = "petzin_test_" + uuid.uuid4().hex
        if ddl is None:
            ddl = MIGRATION.read_text(encoding="utf-8") if MIGRATION.exists() else ""
        sql = (
            "\\set VERBOSITY verbose\n"
            f"BEGIN; CREATE SCHEMA {schema}; "
            f"SET LOCAL search_path TO {schema};\n"
            + ddl
            + "\n"
            + statement
            + "\nROLLBACK;\n"
        )
        env = dict(os.environ, PGCLIENTENCODING="UTF8", PGCONNECT_TIMEOUT="5")
        return subprocess.run(
            [PSQL, "-X", "-w", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
             "-h", os.environ.get("PGHOST", "localhost"),
             "-p", os.environ.get("PGPORT", "5432"),
             "-U", os.environ.get("PGUSER", "postgres"),
             "-d", os.environ.get("PGDATABASE", "petzin")],
            input=sql, capture_output=True, encoding="utf-8", env=env,
            timeout=20,
        )

    def succeeds(self, sql, expected=None):
        result = self.execute(sql)
        self.assertEqual(result.returncode, 0, result.stderr)
        if expected is not None:
            self.assertEqual(result.stdout.strip(), expected)

    def rejects(self, sql, state):
        result = self.execute(sql)
        self.assertNotEqual(result.returncode, 0, "Operação inválida foi aceita")
        self.assertIn(state, result.stderr, result.stderr)

    @staticmethod
    def fixtures():
        return """
        INSERT INTO dono (nome, telefone) VALUES ('Teste A', '+5592000000000');
        INSERT INTO pet (nome, dono_id, especie_id)
        SELECT 'Pet teste', d.id, e.id FROM dono d CROSS JOIN especie e
        WHERE d.nome = 'Teste A' AND e.codigo = 'cachorro';
        """

    @staticmethod
    def reserve(start="2026-10-20", end="2026-10-22", kennel=1, status="ativa", rate="50.00"):
        return f"""
        INSERT INTO reserva (canil_id, data_entrada, data_saida, tarifa_diaria, status)
        SELECT id, DATE '{start}', DATE '{end}', {rate}, '{status}'
        FROM canil WHERE id = {kennel};
        """

    def test_kennel_identifier_outside_hotel_capacity_is_rejected(self):
        self.rejects("INSERT INTO canil (id) VALUES (16);", "23514")

    def test_simplification_preserves_existing_reservation_reference(self):
        migration = SIMPLIFICATION.read_text(encoding="utf-8") if SIMPLIFICATION.exists() else ""
        legacy = """
        CREATE TABLE canil (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            numero INTEGER NOT NULL UNIQUE CHECK (numero BETWEEN 1 AND 15)
        );
        INSERT INTO canil (numero) SELECT generate_series(1, 15);
        CREATE TABLE reserva (id INTEGER PRIMARY KEY, canil_id INTEGER NOT NULL REFERENCES canil(id));
        INSERT INTO reserva VALUES (901, 5);
        """
        result = self.execute(migration + """
            SELECT r.canil_id, c.id FROM reserva r JOIN canil c ON c.id=r.canil_id;
            SELECT column_name, is_identity FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name='canil';
            """, ddl=legacy)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "5|5\nid|NO")

    def test_species_seed_has_stable_dog_code(self):
        self.succeeds("SELECT nome FROM especie WHERE codigo = 'cachorro';", "Cachorro")

    def test_same_owner_name_and_phone_are_allowed(self):
        self.succeeds("""
        INSERT INTO dono (nome, telefone) VALUES ('Repetido', '+5592000000000'), ('Repetido', '+5592000000000');
        SELECT count(*), count(DISTINCT id) FROM dono WHERE nome = 'Repetido';
        """, "2|2")

    def test_same_day_stay_is_allowed_and_rate_is_exact(self):
        self.succeeds(self.reserve(end="2026-10-20") + "SELECT data_saida = data_entrada, tarifa_diaria::text FROM reserva;", "t|50.00")

    def test_departure_before_arrival_is_rejected(self):
        self.rejects(self.reserve(end="2026-10-19"), "23514")

    def test_nonpositive_rate_is_rejected(self):
        self.rejects(self.reserve(rate="0"), "23514")

    def test_same_day_as_departure_conflicts(self):
        self.rejects(self.reserve() + self.reserve(start="2026-10-22", end="2026-10-24"), "23P01")

    def test_day_after_departure_is_available(self):
        self.succeeds(self.reserve() + self.reserve(start="2026-10-23", end="2026-10-24") + "SELECT count(*) FROM reserva;", "2")

    def test_different_kennels_can_share_dates(self):
        self.succeeds(self.reserve() + self.reserve(kennel=2) + "SELECT count(*) FROM reserva;", "2")

    def test_cancelled_reservation_does_not_block_kennel(self):
        self.succeeds(self.reserve(status="cancelada") + self.reserve() + "SELECT count(*) FROM reserva;", "2")

    def test_duplicate_pet_reservation_link_is_rejected(self):
        link = "INSERT INTO reserva_pet (reserva_id, pet_id) SELECT r.id, p.id FROM reserva r CROSS JOIN pet p;"
        self.rejects(self.fixtures() + self.reserve() + link + link, "23505")

    def test_updating_reservation_cannot_create_conflict(self):
        self.rejects(self.reserve() + self.reserve(start="2026-10-24", end="2026-10-25") + "UPDATE reserva SET data_entrada='2026-10-22' WHERE data_entrada='2026-10-24';", "23P01")

    def test_concurrent_requests_cannot_book_same_kennel(self):
        schema = "petzin_test_" + uuid.uuid4().hex
        command = [PSQL, "-X", "-w", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                   "-h", os.environ.get("PGHOST", "localhost"),
                   "-p", os.environ.get("PGPORT", "5432"),
                   "-U", os.environ.get("PGUSER", "postgres"),
                   "-d", os.environ.get("PGDATABASE", "petzin")]
        env = dict(os.environ, PGCLIENTENCODING="UTF8", PGCONNECT_TIMEOUT="5")

        def run(sql):
            return subprocess.run(command, input=sql, capture_output=True,
                                  encoding="utf-8", env=env, timeout=15)

        setup = (f"BEGIN; CREATE SCHEMA {schema}; SET LOCAL search_path TO {schema};\n"
                 + MIGRATION.read_text(encoding="utf-8") + "\nCOMMIT;")
        first = None
        try:
            result = run(setup)
            self.assertEqual(result.returncode, 0, result.stderr)
            # Permite comprovar que o teste detecta a ausência da proteção.
            if os.environ.get("PETZIN_TEST_DISABLE_EXCLUSION") == "1":
                result = run(f"ALTER TABLE {schema}.reserva DROP CONSTRAINT reserva_canil_sem_sobreposicao;")
                self.assertEqual(result.returncode, 0, result.stderr)
            first = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env)
            first.stdin.write(
                f"SET search_path TO {schema}; BEGIN;\n" + self.reserve()
                + "\n\\echo PRIMEIRA_RESERVA_INSERIDA\nSELECT pg_sleep(1); COMMIT;\n"
            )
            first.stdin.close()
            self.assertEqual(first.stdout.readline().strip(), "PRIMEIRA_RESERVA_INSERIDA")
            second = run(f"\\set VERBOSITY verbose\nSET search_path TO {schema};\n" + self.reserve())
            first.wait(timeout=15)
            self.assertEqual(first.returncode, 0, first.stderr.read())
            self.assertNotEqual(second.returncode, 0, "Duas reservas concorrentes foram confirmadas")
            self.assertIn("23P01", second.stderr)
            result = run(f"SELECT count(*) FROM {schema}.reserva;")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "1")
        finally:
            if first is not None:
                if first.poll() is None:
                    first.kill()
                    first.wait(timeout=5)
                first.stdout.close()
                first.stderr.close()
            # O nome foi gerado por este teste, sem dados fornecidos externamente.
            cleanup = run(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
            self.assertEqual(cleanup.returncode, 0, cleanup.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
