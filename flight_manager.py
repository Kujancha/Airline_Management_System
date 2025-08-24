# flight_manager.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QDateTimeEdit, QLabel
)
from PyQt5.QtCore import Qt, QDateTime
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


class FlightManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flights Management")
        self.setGeometry(250, 140, 1100, 650)

        # soft background
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(245, 248, 252))
        self.setPalette(pal)

        root = QVBoxLayout()
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # Title
        title = QLabel("🛫 Flights")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color:#0d47a1;")
        root.addWidget(title, alignment=Qt.AlignLeft)

        # --- Form Card ---
        form_card = QGroupBox("Add Flight")
        form_card.setStyleSheet(CARD_CSS)
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.flight_number = QLineEdit(); self.flight_number.setPlaceholderText("e.g., AI101")
        self.source = QLineEdit(); self.source.setPlaceholderText("e.g., Kathmandu")
        self.destination = QLineEdit(); self.destination.setPlaceholderText("e.g., Delhi")

        self.departure = QDateTimeEdit(QDateTime.currentDateTime())
        self.departure.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.departure.setCalendarPopup(True)

        self.arrival = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))
        self.arrival.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.arrival.setCalendarPopup(True)

        self.seats = QLineEdit(); self.seats.setPlaceholderText("e.g., 180")

        form_layout.addRow("Flight #", self.flight_number)
        form_layout.addRow("Source", self.source)
        form_layout.addRow("Destination", self.destination)
        form_layout.addRow("Departure", self.departure)
        form_layout.addRow("Arrival", self.arrival)
        form_layout.addRow("Seats", self.seats)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add Flight"); add_btn.setStyleSheet(BTN_CSS)
        del_btn = QPushButton("Delete Selected"); del_btn.setStyleSheet(BTN_CSS)
        btn_row.addWidget(add_btn); btn_row.addWidget(del_btn)
        form_layout.addRow(btn_row)

        form_card.setLayout(form_layout)
        root.addWidget(form_card)

        # --- Table Card ---
        table_card = QGroupBox("Flights List")
        table_card.setStyleSheet(CARD_CSS)
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Flight#", "Source", "Destination", "Departure", "Arrival", "Seats"]
        )
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
        add_btn.clicked.connect(self.add_flight)
        del_btn.clicked.connect(self.delete_flight)

        self.load_flights()

    def load_flights(self):
        self.table.setRowCount(0)
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM flights ORDER BY flight_id DESC")
        rows = cur.fetchall()
        for r, row in enumerate(rows):
            self.table.insertRow(r)
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
        con.close()
        self.table.resizeColumnsToContents()

    def add_flight(self):
        try:
            fn = self.flight_number.text().strip()
            src = self.source.text().strip()
            dest = self.destination.text().strip()
            dep = self.departure.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            arr = self.arrival.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            seats = self.seats.text().strip()

            if not (fn and src and dest and seats.isdigit()):
                QMessageBox.warning(self, "Invalid Input", "Please fill all fields correctly.")
                return

            con = db_connect()
            cur = con.cursor()
            cur.execute("""
                INSERT INTO flights (flight_number, source, destination, departure_time, arrival_time, seats)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fn, src, dest, dep, arr, int(seats)))
            con.commit(); con.close()

            self.flight_number.clear(); self.source.clear(); self.destination.clear(); self.seats.clear()
            self.departure.setDateTime(QDateTime.currentDateTime())
            self.arrival.setDateTime(QDateTime.currentDateTime().addSecs(3600))
            self.load_flights()
            QMessageBox.information(self, "Success", "Flight added.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_flight(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Select a flight row to delete.")
            return
        flight_id = self.table.item(row, 0).text()
        try:
            con = db_connect(); cur = con.cursor()
            cur.execute("DELETE FROM flights WHERE flight_id=%s", (flight_id,))
            con.commit(); con.close()
            self.load_flights()
            QMessageBox.information(self, "Deleted", "Flight deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
