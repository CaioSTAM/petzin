import os
import psycopg
from psycopg.rows import dict_row


LOCAL_DATABASE = "host=localhost port=5432 dbname=petzin user=postgres connect_timeout=5"


def get_connection() -> psycopg.Connection:
    """Usar com `with` para confirmar ou desfazer e fechar ao terminar."""
    connection_string = os.getenv("DATABASE_URL", LOCAL_DATABASE)
    return psycopg.connect(connection_string, row_factory=dict_row)
