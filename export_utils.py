import csv
from pathlib import Path

def export_rows_to_csv(rows, filepath: str):
    path = Path(filepath)
    if not rows:
        # crea comunque il file con header standard
        headers = [
            "taratassi","villaggio","consenso_informato","consenso_orale_testimone",
            "eta_mesi_dichiarata", "eta_mesi_stimata", "sesso","muac_cm","peso","altezza","q1","q2","q3","q4","q5","created_at"
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
