# booking_manager.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QRadioButton, QButtonGroup, QLabel
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


class BookingManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bookings Management")
        self.setGeometry(270, 160, 1100, 640)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(245, 248, 252))
        self.setPalette(pal)

        root = QVBoxLayout()
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        title = QLabel("📑 Bookings")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color:#0d47a1;")
        root.addWidget(title, alignment=Qt.AlignLeft)

        # Form
        form_card = QGroupBox("Create Booking"); form_card.setStyleSheet(CARD_CSS)
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.passenger_id = QLineEdit(); self.passenger_id.setPlaceholderText("Passenger ID (number)")
        self.flight_id = QLineEdit(); self.flight_id.setPlaceholderText("Outbound Flight ID (number)")

        # Trip type
        trip_row = QHBoxLayout()
        self.oneway_radio = QRadioButton("One-way"); self.oneway_radio.setChecked(True)
        self.roundtrip_radio = QRadioButton("Round-trip")
        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.oneway_radio)
        self.btn_group.addButton(self.roundtrip_radio)
        trip_row.addWidget(self.oneway_radio); trip_row.addWidget(self.roundtrip_radio)

        self.return_flight_id = QLineEdit(); self.return_flight_id.setPlaceholderText("Return Flight ID (number)")
        self.return_flight_id.setVisible(False)
        self.roundtrip_radio.toggled.connect(lambda checked: self.return_flight_id.setVisible(checked))

        form_layout.addRow("Passenger ID", self.passenger_id)
        form_layout.addRow("Outbound Flight ID", self.flight_id)
        form_layout.addRow("Trip Type", trip_row)
        form_layout.addRow("", self.return_flight_id)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Book"); add_btn.setStyleSheet(BTN_CSS)
        del_btn = QPushButton("Cancel Selected"); del_btn.setStyleSheet(BTN_CSS)
        btn_row.addWidget(add_btn); btn_row.addWidget(del_btn)
        form_layout.addRow(btn_row)

        form_card.setLayout(form_layout)
        root.addWidget(form_card)

        # Table
        table_card = QGroupBox("Bookings List"); table_card.setStyleSheet(CARD_CSS)
        table_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Booking ID", "Passenger ID", "Flight ID", "Date"])
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
        add_btn.clicked.connect(self.book_flight)
        del_btn.clicked.connect(self.cancel_booking)

        self.load_bookings()

    def load_bookings(self):
        self.table.setRowCount(0)
        con = db_connect(); cur = con.cursor()
        cur.execute("SELECT * FROM bookings ORDER BY booking_id DESC")
        rows = cur.fetchall()
        for r, row in enumerate(rows):
            self.table.insertRow(r)
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
        con.close()
        self.table.resizeColumnsToContents()

    def book_flight(self):
        try:
            passenger_id = self.passenger_id.text().strip()
            flight_id = self.flight_id.text().strip()
            is_roundtrip = self.roundtrip_radio.isChecked()

            if not (passenger_id.isdigit() and flight_id.isdigit()):
                QMessageBox.warning(self, "Invalid Input", "Enter valid numeric Passenger ID and Flight ID.")
                return

            con = db_connect(); cur = con.cursor()

            # Outbound seat check
            cur.execute("SELECT seats FROM flights WHERE flight_id=%s", (flight_id,))
            r = cur.fetchone()
            if not r or r[0] < 1:
                QMessageBox.warning(self, "No Seats", "No seats available for outbound flight.")
                con.close(); return

            # Book outbound
            cur.execute("INSERT INTO bookings (passenger_id, flight_id) VALUES (%s, %s)",
                        (int(passenger_id), int(flight_id)))
            cur.execute("UPDATE flights SET seats = seats - 1 WHERE flight_id=%s", (flight_id,))

            # Round-trip
            if is_roundtrip:
                return_flight_id = self.return_flight_id.text().strip()
                if not return_flight_id.isdigit():
                    QMessageBox.warning(self, "Invalid Input", "Enter valid Return Flight ID.")
                    con.rollback(); con.close(); return

                cur.execute("SELECT seats FROM flights WHERE flight_id=%s", (return_flight_id,))
                rr = cur.fetchone()
                if not rr or rr[0] < 1:
                    QMessageBox.warning(self, "No Seats", "No seats available for return flight.")
                    con.rollback(); con.close(); return

                cur.execute("INSERT INTO bookings (passenger_id, flight_id) VALUES (%s, %s)",
                            (int(passenger_id), int(return_flight_id)))
                cur.execute("UPDATE flights SET seats = seats - 1 WHERE flight_id=%s", (return_flight_id,))

            con.commit(); con.close()
            self.passenger_id.clear(); self.flight_id.clear(); self.return_flight_id.clear()
            self.load_bookings()
            QMessageBox.information(self, "Success", "Booking created.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def cancel_booking(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Select a booking row to cancel.")
            return
        booking_id = self.table.item(row, 0).text()
        flight_id = self.table.item(row, 2).text()
        try:
            con = db_connect(); cur = con.cursor()
            cur.execute("DELETE FROM bookings WHERE booking_id=%s", (booking_id,))
            cur.execute("UPDATE flights SET seats = seats + 1 WHERE flight_id=%s", (flight_id,))
            con.commit(); con.close()
            self.load_bookings()
            QMessageBox.information(self, "Cancelled", "Booking cancelled.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
