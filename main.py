import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QDialog
)
from PySide6.QtCore import Qt

from db import init_db, insert_registro, list_registro, get_registro, update_registro
from export_utils import export_rows_to_csv


YES_NO_NS = ["-", "Sì", "No", "Non so"]
YES_NO = ["-", 'Sì', 'No']
VILLAGGI = ["-", "Befandefa", "Andavadoaka"]
SESSI = ["-", "Maschio", "Femmina"]


def bool_to_int(v: bool) -> int:
    return 1 if v else 0


class FormTab(QWidget):
    def __init__(self, on_saved_callback):
        super().__init__()
        self.on_saved_callback = on_saved_callback
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)

        # Taratassi
        self.taratassi = QLineEdit()
        lay.addLayout(self._row("N° Taratassi", self.taratassi))

        # Villaggio
        self.villaggio = QComboBox()
        self.villaggio.addItems(VILLAGGI)
        lay.addLayout(self._row("Villaggio screening", self.villaggio))

        # Consensi
        self.consenso_informato = QCheckBox("Sì")
        self.consenso_orale_testimone = QCheckBox("Sì")
        lay.addWidget(QLabel("Spiegazione consenso informato"))
        lay.addWidget(self.consenso_informato)
        lay.addWidget(QLabel("Consenso orale con testimone"))
        lay.addWidget(self.consenso_orale_testimone)

        # Età mesi dichiarata
        self.eta_mesi_dichiarata = QSpinBox()
        self.eta_mesi_dichiarata.setRange(0, 2400)
        lay.addLayout(self._row("Età in mesi dichiarata", self.eta_mesi_dichiarata))

        # Età mesi stimata
        self.eta_mesi_stimata = QSpinBox()
        self.eta_mesi_stimata.setRange(0, 2400)
        lay.addLayout(self._row("Età in mesi stimata", self.eta_mesi_stimata))

        # Sesso
        self.sesso = QComboBox()
        self.sesso.addItems(SESSI)
        lay.addLayout(self._row("Sesso", self.sesso))

        # Misure
        self.muac = QDoubleSpinBox()
        self.muac.setRange(0, 1000)
        self.muac.setDecimals(2)
        self.muac.setSingleStep(0.1)
        lay.addLayout(self._row("Circonferenza braccio (MUAC) cm", self.muac))

        self.peso = QDoubleSpinBox()
        self.peso.setRange(0, 1000)
        self.peso.setDecimals(2)
        self.peso.setSingleStep(0.1)
        lay.addLayout(self._row("Peso (Kg)", self.peso))

        self.altezza = QDoubleSpinBox()
        self.altezza.setRange(0, 300)
        self.altezza.setDecimals(0)
        self.altezza.setSingleStep(0.1)
        lay.addLayout(self._row("Altezza (cm)", self.altezza))

        # Domande
        self.q1 = QComboBox(); self.q1.addItems(YES_NO_NS)
        self.q2 = QComboBox(); self.q2.addItems(YES_NO)
        self.q3 = QComboBox(); self.q3.addItems(YES_NO_NS)
        self.q4 = QComboBox(); self.q4.addItems(YES_NO_NS)
        self.q5 = QComboBox(); self.q5.addItems(YES_NO)

        lay.addLayout(self._row("Negli ultimi 7 giorni ha mangiato meno/rifiutato cibo?", self.q1))
        lay.addLayout(self._row("Ieri ha mangiato almeno 3 volte (oltre al latte)?", self.q2))
        lay.addLayout(self._row("Diarrea ultime 2 settimane?", self.q3))
        lay.addLayout(self._row("Febbre ultime 2 settimane?", self.q4))
        lay.addLayout(self._row("Prende ancora latte materno?", self.q5))

        # Pulsanti
        btns = QHBoxLayout()
        self.save_btn = QPushButton("Salva compilazione")
        self.clear_btn = QPushButton("Svuota form")
        btns.addWidget(self.save_btn)
        btns.addWidget(self.clear_btn)
        lay.addLayout(btns)

        self.save_btn.clicked.connect(self._save)
        self.clear_btn.clicked.connect(self._clear)

        lay.addStretch(1)

    def _row(self, label, widget):
        r = QHBoxLayout()
        r.addWidget(QLabel(label))
        r.addWidget(widget, 1)
        return r

    def _clear(self):
        self.taratassi.setText("")
        self.villaggio.setCurrentIndex(0)
        self.consenso_informato.setChecked(False)
        self.consenso_orale_testimone.setChecked(False)
        self.eta_mesi_dichiarata.setValue(0)
        self.eta_mesi_stimata.setValue(0)
        self.sesso.setCurrentIndex(0)
        self.muac.setValue(0)
        self.peso.setValue(0)
        self.altezza.setValue(0)
        self.q1.setCurrentIndex(0)
        self.q2.setCurrentIndex(0)
        self.q3.setCurrentIndex(0)
        self.q4.setCurrentIndex(0)
        self.q5.setCurrentIndex(0)

    def _save(self):
        tar = self.taratassi.text().strip()
        if not tar:
            QMessageBox.warning(self, "Errore", "N° Taratassi è obbligatorio.")
            return

        data = {
            "taratassi": tar,
            "villaggio": self.villaggio.currentText(),
            "consenso_informato": bool_to_int(self.consenso_informato.isChecked()),
            "consenso_orale_testimone": bool_to_int(self.consenso_orale_testimone.isChecked()),
            "eta_mesi_dichiarata": int(self.eta_mesi_dichiarata.value()),
            "eta_mesi_stimata": int(self.eta_mesi_stimata.value()),
            "sesso": self.sesso.currentText(),
            "muac_cm": float(self.muac.value()) if self.muac.value() != 0 else None,
            "peso": float(self.peso.value()) if self.peso.value() != 0 else None,
            "altezza": float(self.altezza.value()) if self.altezza.value() != 0 else None,
            "q1": self.q1.currentText(),
            "q2": self.q2.currentText(),
            "q3": self.q3.currentText(),
            "q4": self.q4.currentText(),
            "q5": self.q5.currentText(),
        }

        for key, value in data.items():
            if not value or value == '-':
                QMessageBox.warning(self, "Errore", f"{key} è obbligatorio.")
                return

        try:
            insert_registro(data)
        except Exception as e:
            QMessageBox.critical(self, "Errore salvataggio", str(e))
            return

        QMessageBox.information(self, "OK", "Compilazione salvata correttamente.")
        self.on_saved_callback()
        self._clear()

class EditDialog(QDialog):
    def __init__(self, taratassi: str, parent=None):
        super().__init__(parent)
        self.taratassi_value = taratassi
        self.setWindowTitle(f"Modifica: {taratassi}")
        self.resize(700, 600)
        self._build()
        self._load()

    def _build(self):
        lay = QVBoxLayout(self)

        # Taratassi (solo lettura)
        self.taratassi = QLineEdit()
        self.taratassi.setReadOnly(True)
        lay.addLayout(self._row("N° Taratassi", self.taratassi))

        self.villaggio = QComboBox(); self.villaggio.addItems(VILLAGGI)
        lay.addLayout(self._row("Villaggio screening", self.villaggio))

        self.consenso_informato = QCheckBox("Sì (spuntato = Sì)")
        self.consenso_orale_testimone = QCheckBox("Sì (spuntato = Sì)")
        lay.addWidget(QLabel("Spiegazione consenso informato (Sì/No)"))
        lay.addWidget(self.consenso_informato)
        lay.addWidget(QLabel("Consenso orale con testimone (Sì/No)"))
        lay.addWidget(self.consenso_orale_testimone)

        # Età mesi dichiarata
        self.eta_mesi_dichiarata = QSpinBox()
        self.eta_mesi_dichiarata.setRange(0, 2400)
        lay.addLayout(self._row("Età in mesi dichiarata", self.eta_mesi_dichiarata))

        # Età mesi stimata
        self.eta_mesi_stimata = QSpinBox()
        self.eta_mesi_stimata.setRange(0, 2400)
        lay.addLayout(self._row("Età in mesi stimata", self.eta_mesi_stimata))

        self.sesso = QComboBox(); self.sesso.addItems(SESSI)
        lay.addLayout(self._row("Sesso", self.sesso))

        self.muac = QDoubleSpinBox(); self.muac.setRange(0, 1000); self.muac.setDecimals(2); self.muac.setSingleStep(0.1)
        lay.addLayout(self._row("Circonferenza braccio (MUAC) cm", self.muac))

        self.peso = QDoubleSpinBox(); self.peso.setRange(0, 1000); self.peso.setDecimals(2); self.peso.setSingleStep(0.1)
        lay.addLayout(self._row("Peso", self.peso))

        self.altezza = QDoubleSpinBox(); self.altezza.setRange(0, 300); self.altezza.setDecimals(2); self.altezza.setSingleStep(0.1)
        lay.addLayout(self._row("Altezza", self.altezza))

        self.q1 = QComboBox(); self.q1.addItems(YES_NO_NS)
        self.q2 = QComboBox(); self.q2.addItems(YES_NO_NS)
        self.q3 = QComboBox(); self.q3.addItems(YES_NO_NS)
        self.q4 = QComboBox(); self.q4.addItems(YES_NO_NS)
        self.q5 = QComboBox(); self.q5.addItems(YES_NO_NS)

        lay.addLayout(self._row("Negli ultimi 7 giorni ha mangiato meno/rifiutato cibo?", self.q1))
        lay.addLayout(self._row("Ieri ha mangiato almeno 3 volte (oltre al latte)?", self.q2))
        lay.addLayout(self._row("Diarrea ultime 2 settimane?", self.q3))
        lay.addLayout(self._row("Febbre ultime 2 settimane?", self.q4))
        lay.addLayout(self._row("Prende ancora latte materno?", self.q5))

        btns = QHBoxLayout()
        self.save_btn = QPushButton("Salva modifiche")
        self.cancel_btn = QPushButton("Annulla")
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        lay.addLayout(btns)

        self.save_btn.clicked.connect(self._save)
        self.cancel_btn.clicked.connect(self.reject)

    def _row(self, label, widget):
        r = QHBoxLayout()
        r.addWidget(QLabel(label))
        r.addWidget(widget, 1)
        return r

    def _load(self):
        row = get_registro(self.taratassi_value)
        if not row:
            QMessageBox.critical(self, "Errore", "Record non trovato.")
            self.reject()
            return

        self.taratassi.setText(row["taratassi"])
        self.villaggio.setCurrentText(row["villaggio"])
        self.consenso_informato.setChecked(row["consenso_informato"] == 1)
        self.consenso_orale_testimone.setChecked(row["consenso_orale_testimone"] == 1)
        self.eta_mesi_dichiarata.setValue(int(row["eta_mesi_dichiarata"] or 0))
        self.eta_mesi_stimata.setValue(int(row["eta_mesi_dichiarata"] or 0))
        self.sesso.setCurrentText(row["sesso"])
        self.muac.setValue(float(row["muac_cm"] or 0))
        self.peso.setValue(float(row["peso"] or 0))
        self.altezza.setValue(float(row["altezza"] or 0))
        self.q1.setCurrentText(row["q1"])
        self.q2.setCurrentText(row["q2"])
        self.q3.setCurrentText(row["q3"])
        self.q4.setCurrentText(row["q4"])
        self.q5.setCurrentText(row["q5"])

    def _save(self):
        data = {
            "villaggio": self.villaggio.currentText(),
            "consenso_informato": 1 if self.consenso_informato.isChecked() else 0,
            "consenso_orale_testimone": 1 if self.consenso_orale_testimone.isChecked() else 0,
            "eta_mesi_dichiarata": int(self.eta_mesi_dichiarata.value()),
            "eta_mesi_stimata": int(self.eta_mesi_stimata.value()),
            "sesso": self.sesso.currentText(),
            "muac_cm": float(self.muac.value()) if self.muac.value() != 0 else None,
            "peso": float(self.peso.value()) if self.peso.value() != 0 else None,
            "altezza": float(self.altezza.value()) if self.altezza.value() != 0 else None,
            "q1": self.q1.currentText(),
            "q2": self.q2.currentText(),
            "q3": self.q3.currentText(),
            "q4": self.q4.currentText(),
            "q5": self.q5.currentText(),
        }

        try:
            update_registro(self.taratassi_value, data)
        except Exception as e:
            QMessageBox.critical(self, "Errore salvataggio", str(e))
            return

        QMessageBox.information(self, "OK", "Modifiche salvate.")
        self.accept()

class ResultsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build()
        self.refresh()

    def _build(self):
        lay = QVBoxLayout(self)

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Cerca Taratassi...")
        self.refresh_btn = QPushButton("Aggiorna")
        self.export_btn = QPushButton("Esporta CSV")
        self.edit_btn = QPushButton("Modifica selezionato")
        top.addWidget(self.edit_btn)

        top.addWidget(self.search, 1)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.export_btn)
        lay.addLayout(top)

        self.table = QTableWidget()
        lay.addWidget(self.table, 1)

        self.refresh_btn.clicked.connect(self.refresh)
        self.search.textChanged.connect(self.refresh)
        self.export_btn.clicked.connect(self.export_csv)
        self.edit_btn.clicked.connect(self.edit_selected)
        self.table.cellDoubleClicked.connect(self.edit_selected)

    def refresh(self):
        rows = list_registro(self.search.text())
        self._fill(rows)

    def _fill(self, rows):
        headers = [
            "taratassi", "villaggio", "eta_mesi_dichiarata", "eta_mesi_stimata", "sesso",
            "muac_cm", "peso", "altezza",
            "consenso_informato", "consenso_orale_testimone",
            "q1","q2","q3","q4","q5",
            "created_at"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))

        for r_i, r in enumerate(rows):
            for c_i, h in enumerate(headers):
                v = r[h]
                if h in ("consenso_informato", "consenso_orale_testimone"):
                    v = "Sì" if v == 1 else "No"
                item = QTableWidgetItem("" if v is None else str(v))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # sola lettura
                self.table.setItem(r_i, c_i, item)

        self.table.resizeColumnsToContents()

    def export_csv(self):
        rows = list_registro(self.search.text())
        path, _ = QFileDialog.getSaveFileName(self, "Salva CSV", "risultati.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            export_rows_to_csv(rows, path)
            QMessageBox.information(self, "OK", "CSV esportato correttamente.")
        except Exception as e:
            QMessageBox.critical(self, "Errore export", str(e))

    def _selected_taratassi(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)  # colonna taratassi
        return item.text().strip() if item else None

    def edit_selected(self, *_):
        tar = self._selected_taratassi()
        if not tar:
            QMessageBox.warning(self, "Attenzione", "Seleziona una riga da modificare.")
            return

        dlg = EditDialog(tar, self)
        if dlg.exec():
            self.refresh()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Questionario Taratassi (Offline)")
        self.resize(1100, 700)

        lay = QVBoxLayout(self)
        self.tabs = QTabWidget()
        lay.addWidget(self.tabs)

        self.results_tab = ResultsTab()
        self.form_tab = FormTab(on_saved_callback=self.results_tab.refresh)

        self.tabs.addTab(self.form_tab, "Nuova compilazione")
        self.tabs.addTab(self.results_tab, "Risultati")


def main():
    init_db()
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
