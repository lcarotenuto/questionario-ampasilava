import csv
from pathlib import Path


BOOLEAN_FIELDS = {"consent", "witnessed"}


def csv_value(value, field_name=None):
    if field_name in BOOLEAN_FIELDS:
        if value == 1:
            return "Sì"
        if value == 0:
            return "No"
        return ""
    return "" if value is None else value


def export_rows_to_csv(rows, filepath: str):
    path = Path(filepath)
    headers = [
        "taratassi", "village", "consent", "witnessed",
        "declared_age", "age_estimation", "gender", "muac", "weight", "height", "q1", "q2", "q3", "q4", "q5",
        "created_at"
    ]
    header_label = [
        'Taratassi', 'Villaggio', 'Spiegazione consenso informato', 'Consenso orale con testimone',
        'Età Dichiarata', 'Età Stimata', 'Sesso', 'MUAC', 'Peso (KG)', 'Altezza (cm)',
        'Indice WHZ', 'Domanda 1', 'Domanda 2', 'Domanda 3', 'Domanda 4', 'Domanda 5', 'Data creazione'
    ]

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header_label)
        for r in rows:
            writer.writerow([
                csv_value(r[h], h) for h in headers
            ])
