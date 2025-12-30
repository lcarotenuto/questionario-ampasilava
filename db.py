import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("questionario.sqlite3")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registro (
                taratassi TEXT PRIMARY KEY,
                villaggio TEXT NOT NULL CHECK (villaggio IN ('Andavadoaka','Befandefa')),
                consenso_informato INTEGER NOT NULL CHECK (consenso_informato IN (0,1)),
                consenso_orale_testimone INTEGER NOT NULL CHECK (consenso_orale_testimone IN (0,1)),
                eta_mesi_dichiarata INTEGER NOT NULL CHECK (eta_mesi_dichiarata >= 0),
                eta_mesi_stimata INTEGER NOT NULL CHECK (eta_mesi_stimata >= 0),
                sesso TEXT NOT NULL CHECK (sesso IN ('Maschio','Femmina')),
                muac_cm REAL,
                peso REAL,
                altezza REAL,
                q1 TEXT NOT NULL CHECK (q1 IN ('Sì','No','Non so')),
                q2 TEXT NOT NULL CHECK (q2 IN ('Sì','No','Non so')),
                q3 TEXT NOT NULL CHECK (q3 IN ('Sì','No','Non so')),
                q4 TEXT NOT NULL CHECK (q4 IN ('Sì','No','Non so')),
                q5 TEXT NOT NULL CHECK (q5 IN ('Sì','No','Non so')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )


def insert_registro(data: dict):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO registro (
              taratassi, villaggio, consenso_informato, consenso_orale_testimone,
              eta_mesi_dichiarata, eta_mesi_stimata, sesso, muac_cm, peso, altezza,
              q1, q2, q3, q4, q5
            ) VALUES (
              :taratassi, :villaggio, :consenso_informato, :consenso_orale_testimone,
              :eta_mesi_dichiarata, :eta_mesi_stimata, :sesso, :muac_cm, :peso, :altezza,
              :q1, :q2, :q3, :q4, :q5
            )
            """,
            data,
        )


def list_registro(search: str = ""):
    q = """
    SELECT *
    FROM registro
    WHERE taratassi LIKE ?
    ORDER BY created_at DESC
    """
    like = f"%{search.strip()}%"
    with get_conn() as conn:
        return conn.execute(q, (like,)).fetchall()


def get_registro(taratassi: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM registro WHERE taratassi = ?",
            (taratassi,),
        ).fetchone()


def update_registro(taratassi: str, data: dict):
    # taratassi resta chiave primaria e NON viene modificato
    data = dict(data)
    data["taratassi"] = taratassi
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE registro SET
              villaggio = :villaggio,
              consenso_informato = :consenso_informato,
              consenso_orale_testimone = :consenso_orale_testimone,
              eta_mesi_dichiarata = :eta_mesi_dichiarata,
              eta_mesi_stimata = :eta_mesi_stimata,
              sesso = :sesso,
              muac_cm = :muac_cm,
              peso = :peso,
              altezza = :altezza,
              q1 = :q1, q2 = :q2, q3 = :q3, q4 = :q4, q5 = :q5
            WHERE taratassi = :taratassi
            """,
            data,
        )
