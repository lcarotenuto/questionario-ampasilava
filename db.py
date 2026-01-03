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
            CREATE TABLE IF NOT EXISTS registro (
                taratassi TEXT PRIMARY KEY,
                villaggio TEXT NOT NULL CHECK (villaggio IN ('Andavadoaka','Befandefa')),
                consenso_informato INTEGER NOT NULL CHECK (consenso_informato IN (0,1)),
                consenso_orale_testimone INTEGER NOT NULL CHECK (consenso_orale_testimone IN (0,1)),
                eta_mesi_dichiarata INTEGER NOT NULL CHECK (eta_mesi_dichiarata >= 0),
                eta_mesi_stimata INTEGER NOT NULL CHECK (eta_mesi_stimata >= 0),
                sesso TEXT NOT NULL CHECK (sesso IN ('Maschio','Femmina')),
                muac_cm REAL NOT NULL,
                peso REAL NOT NULL,
                altezza REAL NOT NULL,
                wmz REAL,
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
              eta_mesi_dichiarata, eta_mesi_stimata, sesso, muac_cm, peso, altezza, wmz,
              q1, q2, q3, q4, q5
            ) VALUES (
              :taratassi, :villaggio, :consenso_informato, :consenso_orale_testimone,
              :eta_mesi_dichiarata, :eta_mesi_stimata, :sesso, :muac_cm, :peso, :altezza, :wmz
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
              wmz = :wmz,
              q1 = :q1, q2 = :q2, q3 = :q3, q4 = :q4, q5 = :q5
            WHERE taratassi = :taratassi
            """,
            data,
        )
