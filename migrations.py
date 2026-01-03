import sqlite3
from typing import Callable, Dict

CURRENT_SCHEMA_VERSION = 1  # <-- quando fai modifiche, aumentala a 2, 3, ...

MigrationFn = Callable[[sqlite3.Connection], None]


def ensure_version_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        )
    """)
    # crea la riga (id=1) se non esiste
    conn.execute("""
        INSERT INTO schema_version (id, version)
        VALUES (1, 1)
        ON CONFLICT(id) DO NOTHING
    """)


def get_db_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT version FROM schema_version WHERE id = 1").fetchone()
    return int(row[0]) if row else 1


def set_db_version(conn: sqlite3.Connection, version: int) -> None:
    conn.execute("UPDATE schema_version SET version = ? WHERE id = 1", (version,))

# --- MIGRAZIONI ---

MIGRATIONS: Dict[int, MigrationFn] = {
    # 2: migration_1_to_2,  # "per arrivare alla versione 2"
}


def migrate_if_needed(conn: sqlite3.Connection) -> None:
    """
    Porta il DB alla versione CURRENT_SCHEMA_VERSION.
    Esegue migrazioni incrementalmente: v->v+1.
    """
    # transazione unica
    with conn:
        ensure_version_table(conn)
        db_version = get_db_version(conn)

        if db_version > CURRENT_SCHEMA_VERSION:
            raise RuntimeError(
                f"DB version {db_version} > app version {CURRENT_SCHEMA_VERSION}. "
                "Hai una app più vecchia del database."
            )

        while db_version < CURRENT_SCHEMA_VERSION:
            next_version = db_version + 1
            fn = MIGRATIONS.get(next_version)
            if not fn:
                raise RuntimeError(f"Migrazione mancante per arrivare alla versione {next_version}")

            fn(conn)
            set_db_version(conn, next_version)
            db_version = next_version