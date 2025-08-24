# passenger_manager.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
from db_utils import db_connect

BTN_CSS = """
QPushButton {
    font-size: 14px; padding: 10px 16px;
    border-radius: 8px; background-color: #1976d2; color: white;
}
QPushButton:hover { background-color: #1565c0; }
QPushButton:pressed { background-color: #0d47a1; }
"""

CARD_CSS = """
QGroupBox {
    border: 1px solid #e0e0e0; border-radius: 10px; margin-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin; left: 12px; padding: 0 6px;
    color:#0d47a1; font-weight:600;
}
"""


class PassengerManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Passengers Management")
        self.setGeometry(260, 150, 1000, 630)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(245, 248, 252))
        self.setPalette(pal)

        root = QVBoxLayout()
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        title = QLabel("👤 Passengers")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color:#0d47a1;")
        root.addWidget(title, alignment=Qt.AlignLeft)

        # Form
        form_card = QGroupBox("Add Passenger"); form_card.setStyleSheet(CARD_CSS)
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.name = QLineEdit(); self.name.setPlaceholderText("Full name")
        self.gender = QLineEdit(); self.gender.setPlaceholderText("Gender")
        self.age = QLineEdit(); self.age.setPlaceholderText("Age (number)")
        self.passport_no = QLineEdit(); self.passport_no.setPlaceholderText("Passport No")

        form_layout.addRow("Name", self.name)
        form_layout.addRow("Gender", self.gender)
        form_layout.addRow("Age", self.age)
        form_layout.addRow("Passport No", self.passport_no)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add Passenger"); add_btn.setStyleSheet(BTN_CSS)
        del_btn = QPushButton("Delete Selected"); del_btn.setStyleSheet(BTN_CSS)
        btn_row.addWidget(add_btn); btn_row.addWidget(del_btn)
        form_layout.addRow(btn_row)
        form_card.setLayout(form_layout)
        root.addWidget(form_card)

        # Table
        table_card = QGroupBox("Passengers List"); table_card.setStyleSheet(CARD_CSS)
        table_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Gender", "Age", "Passport No"])
        self.table.setAlternatingRowColors(True)
        header: QHeaderView = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        table_layout.addWidget(self.table)
        table_card.setLayout(table_layout)
        root.addWidget(table_card, stretch=1)

        self.setLayout(root)

        # signals
        add_btn.clicked.connect(self.add_passenger)
        del_btn.clicked.connect(self.delete_passenger)

        self.load_passengers()

    def load_passengers(self):
        self.table.setRowCount(0)
        con = db_connect(); cur = con.cursor()
        cur.execute("SELECT * FROM passengers ORDER BY passenger_id DESC")
        rows = cur.fetchall()
        for r, row in enumerate(rows):
            self.table.insertRow(r)
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
        con.close()
        self.table.resizeColumnsToContents()

    def add_passenger(self):
        try:
            name = self.name.text().strip()
            gender = self.gender.text().strip()
            age = self.age.text().strip()
            passport_no = self.passport_no.text().strip()

            if not (name and gender and age.isdigit() and passport_no):
                QMessageBox.warning(self, "Invalid Input", "Please fill all fields correctly.")
                return

            con = db_connect(); cur = con.cursor()
            cur.execute("""
                INSERT INTO passengers (name, gender, age, passport_no)
                VALUES (%s, %s, %s, %s)
            """, (name, gender, int(age), passport_no))
            con.commit(); con.close()

            self.name.clear(); self.gender.clear(); self.age.clear(); self.passport_no.clear()
            self.load_passengers()
            QMessageBox.information(self, "Success", "Passenger added.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_passenger(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Select a passenger row to delete.")
            return
        pid = self.table.item(row, 0).text()
        try:
            con = db_connect(); cur = con.cursor()
            cur.execute("DELETE FROM passengers WHERE passenger_id=%s", (pid,))
            con.commit(); con.close()
            self.load_passengers()
            QMessageBox.information(self, "Deleted", "Passenger deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
