# main.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QMenuBar, QAction, QStatusBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont

from flight_manager import FlightManager
from passenger_manager import PassengerManager
from booking_manager import BookingManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Airline Management System")
        self.setGeometry(200, 100, 1100, 700)  # larger, widescreen-friendly

        # --- Light background for a cleaner look ---
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(245, 248, 252))  # soft off-white
        self.setPalette(pal)

        # --- Central content ---
        central = QWidget(self)
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(80, 60, 80, 60)

        # Title
        title = QLabel("✈ Airline Management System")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color:#0d47a1;")  # deep blue
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Manage flights, passengers and bookings")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color:#607d8b;")
        layout.addWidget(subtitle)

        # Spacer-ish
        layout.addStretch(1)

        # Button style (rounded, hover)
        btn_css = """
            QPushButton {
                font-size: 16px;
                padding: 14px 20px;
                border-radius: 10px;
                background-color: #1976d2;
                color: white;
            }
            QPushButton:hover { background-color: #1565c0; }
            QPushButton:pressed { background-color: #0d47a1; }
        """

        # Buttons
        flights_btn = QPushButton("🛫 Manage Flights")
        passengers_btn = QPushButton("👤 Manage Passengers")
        bookings_btn = QPushButton("📑 Manage Bookings")
        for b in (flights_btn, passengers_btn, bookings_btn):
            b.setStyleSheet(btn_css)
            b.setMinimumHeight(48)
            layout.addWidget(b, alignment=Qt.AlignCenter)

        layout.addStretch(2)

        central.setLayout(layout)
        self.setCentralWidget(central)

        # Connect
        flights_btn.clicked.connect(self.open_flights)
        passengers_btn.clicked.connect(self.open_passengers)
        bookings_btn.clicked.connect(self.open_bookings)

        # --- Simple menu bar ---
        self._build_menu()

        # --- Status bar ---
        sb = QStatusBar()
        sb.showMessage("Ready")
        self.setStatusBar(sb)

    def _build_menu(self):
        menubar: QMenuBar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        help_menu = menubar.addMenu("&Help")

        exit_act = QAction("E&xit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        about_act = QAction("&About", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

    def show_about(self):
        QMessageBox.information(
            self,
            "About",
            "Airline Management System\n\nPython (PyQt5) + MySQL demo UI\nManage flights, passengers, and bookings."
        )

    def open_flights(self):
        self.fwin = FlightManager()
        self.fwin.show()

    def open_passengers(self):
        self.pwin = PassengerManager()
        self.pwin.show()

    def open_bookings(self):
        self.bwin = BookingManager()
        self.bwin.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # PyQt5 event loop:
    sys.exit(app.exec_())
