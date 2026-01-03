import csv
from pathlib import Path

def export_rows_to_csv(rows, filepath: str):
    path = Path(filepath)
    if not rows:
        # crea comunque il file con header standard
        headers = [
            "taratassi","village","consent","witnessed",
            "declared_age", "age_estimation", "gender","muac","weight","height","q1","q2","q3","q4","q5","created_at"
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        return

    headers = rows[0].keys()
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            writer.writerow([r[h] for h in headers])
