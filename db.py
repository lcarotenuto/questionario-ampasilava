import sqlite3
import sys
from pathlib import Path

from migrations import migrate_if_needed

APP_DB_FILENAME = "questionario.sqlite3"


def portable_base_dir() -> Path:
    """
    Restituisce la cartella 'accanto' all'eseguibile:
    - Dev mode: cartella del progetto (dove sta db.py)
    - Windows frozen: cartella dell'EXE
    - macOS frozen: cartella che CONTIENE la .app (non dentro la .app)
    """
    if getattr(sys, "frozen", False):
        exe_path = Path(sys.executable).resolve()

        if sys.platform == "darwin":
            # .../MyApp.app/Contents/MacOS/MyApp  -> vogliamo la cartella che contiene MyApp.app
            # parents[0]=MacOS, [1]=Contents, [2]=MyApp.app, [3]=cartella contenente la .app
            return exe_path.parents[3]

        # Windows/Linux: cartella dell'eseguibile
        return exe_path.parent

    # dev mode
    return Path(__file__).resolve().parent


def db_path() -> Path:
    base = portable_base_dir()
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / APP_DB_FILENAME


DB_PATH = db_path()



def get_conn():
    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.OperationalError as e:
        # Tipico su macOS se stai lanciando da DMG / Applications senza permessi
        raise RuntimeError(
            f"Impossibile creare/scrivere il DB in: {DB_PATH}\n"
            f"Assicurati che l'app sia in una cartella scrivibile (Desktop/USB) e che esista 'data/'.\n"
            f"Errore originale: {e}"
        )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        migrate_if_needed(conn)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registry (
                taratassi TEXT PRIMARY KEY UNIQUE,
                village TEXT NOT NULL CHECK (village IN ('Andavadoaka','Befandefa')),
                consent INTEGER NOT NULL CHECK (consent IN (0,1)),
                witnessed INTEGER NOT NULL CHECK (witnessed IN (0,1)),
                declared_age INTEGER NOT NULL CHECK (declared_age >= 0),
                age_estimation INTEGER NOT NULL CHECK (age_estimation >= 0),
                gender TEXT NOT NULL CHECK (gender IN ('Maschio','Femmina')),
                muac REAL NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                whz REAL,
                q1 TEXT NOT NULL CHECK (q1 IN ('Sì','No','Non so')),
                q2 TEXT NOT NULL CHECK (q2 IN ('Sì','No','Non so')),
                q3 TEXT NOT NULL CHECK (q3 IN ('Sì','No','Non so')),
                q4 TEXT NOT NULL CHECK (q4 IN ('Sì','No','Non so')),
                q5 TEXT NOT NULL CHECK (q5 IN ('Sì','No','Non so')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )


def insert_registry(data: dict):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO registry (
              taratassi, village, consent, witnessed,
              declared_age, age_estimation, gender, muac, weight, height, whz,
              q1, q2, q3, q4, q5
            ) VALUES (
              :taratassi, :village, :consent, :witnessed,
              :declared_age, :age_estimation, :gender, :muac, :weight, :height, :whz,
              :q1, :q2, :q3, :q4, :q5
            )
            """,
            data,
        )


def list_registry(search: str = ""):
    q = """
    SELECT *
    FROM registry
    WHERE taratassi LIKE ?
    ORDER BY created_at DESC
    """
    like = f"%{search.strip()}%"
    with get_conn() as conn:
        return conn.execute(q, (like,)).fetchall()


def get_registry(taratassi: str):
    with get_conn() as conn:
        return dict(conn.execute(
            "SELECT * FROM registry WHERE taratassi = ?",
            (taratassi,),
        ).fetchone())


def update_registry(taratassi: str, data: dict):
    # taratassi resta chiave primaria e NON viene modificato
    data = dict(data)
    data["taratassi"] = taratassi
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE registry SET
              village = :village,
              consent = :consent,
              witnessed = :witnessed,
              declared_age = :declared_age,
              age_estimation = :age_estimation,
              gender = :gender,
              muac = :muac,
              weight = :weight,
              height = :height,
              whz = :whz,
              q1 = :q1, q2 = :q2, q3 = :q3, q4 = :q4, q5 = :q5
            WHERE taratassi = :taratassi
            """,
            data,
        )

def delete_registry(taratassi: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM registry WHERE taratassi = ?",
            (taratassi,)
        )
