"""Main window with sidebar navigation."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QStackedWidget, QLabel, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon


class MainWindow:
    """Main application window."""

    def __init__(self):
        self.window = None
        self.stacked_widget = None
        self.sidebar_buttons = {}
        self.current_page = None

    def setup(self, window):
        """Setup main window layout."""
        self.window = window
        
        # Main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)
        
        # Add placeholder pages
        from .patients import PatientsPage
        from .medicines import MedicinesPage
        from .appointments import AppointmentsPage
        from .prescriptions import PrescriptionsPage
        
        self.stacked_widget.addWidget(DashboardPage(self))
        self.stacked_widget.addWidget(PatientsPage(self))
        self.stacked_widget.addWidget(AppointmentsPage(self))
        self.stacked_widget.addWidget(MedicinesPage(self))
        self.stacked_widget.addWidget(PrescriptionsPage(self))
        
        self.window.setLayout(main_layout)
        
        # Show dashboard by default
        self.navigate_to("dashboard")

    def _create_sidebar(self) -> QWidget:
        """Create sidebar navigation."""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #2c3e50;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title
        title = QLabel("CareDesk")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            background-color: #1a252f;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Navigation buttons
        nav_items = [
            ("dashboard", "Dashboard", "🏠"),
            ("patients", "Patients", "👥"),
            ("appointments", "Appointments", "📅"),
            ("medicines", "Medicines", "💊"),
            ("prescriptions", "Prescriptions", "📝"),
        ]
        
        for page_id, label, icon in nav_items:
            btn = self._create_nav_button(label, icon)
            btn.clicked.connect(lambda checked, p=page_id: self.navigate_to(p))
            self.sidebar_buttons[page_id] = btn
            layout.addWidget(btn)
        
        layout.addStretch()
        sidebar.setLayout(layout)
        return sidebar

    def _create_nav_button(self, label: str, icon: str) -> QPushButton:
        """Create a navigation button."""
        btn = QPushButton(f"{icon}  {label}")
        btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                padding: 15px 20px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
            }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def navigate_to(self, page_id: str):
        """Navigate to a specific page."""
        page_map = {
            "dashboard": 0,
            "patients": 1,
            "appointments": 2,
            "medicines": 3,
            "prescriptions": 4,
        }
        
        if page_id in page_map:
            # Reset all button states
            for btn in self.sidebar_buttons.values():
                btn.setChecked(False)
            
            # Set active button
            if page_id in self.sidebar_buttons:
                self.sidebar_buttons[page_id].setChecked(True)
            
            # Switch page
            self.stacked_widget.setCurrentIndex(page_map[page_id])
            self.current_page = page_id
            
            # Refresh page data
            widget = self.stacked_widget.currentWidget()
            if hasattr(widget, 'refresh'):
                widget.refresh()

    def show_message(self, title: str, message: str, 
                    icon: QMessageBox.Icon = QMessageBox.Icon.Information):
        """Show a message box."""
        msg = QMessageBox(self.window)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    def show_error(self, title: str, message: str):
        """Show an error message."""
        self.show_message(title, message, QMessageBox.Icon.Critical)


class DashboardPage(QWidget):
    """Dashboard page with overview statistics."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        """Setup dashboard UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.stats = {
            'patients': self._create_stat_card("Total Patients", "0", "#3498db"),
            'appointments': self._create_stat_card("Today's Appointments", "0", "#2ecc71"),
            'medicines': self._create_stat_card("Medicines", "0", "#9b59b6"),
            'prescriptions': self._create_stat_card("Prescriptions", "0", "#e74c3c"),
        }
        
        for stat in self.stats.values():
            stats_layout.addWidget(stat)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        add_patient_btn = QPushButton("➕ Add Patient")
        add_medicine_btn = QPushButton("💊 Add Medicine")
        new_appointment_btn = QPushButton("📅 New Appointment")
        new_prescription_btn = QPushButton("📝 New Prescription")
        
        for btn in [add_patient_btn, add_medicine_btn, new_appointment_btn, new_prescription_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 20px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        add_patient_btn.clicked.connect(lambda: self.main_window.navigate_to("patients"))
        add_medicine_btn.clicked.connect(lambda: self.main_window.navigate_to("medicines"))
        new_appointment_btn.clicked.connect(lambda: self.main_window.navigate_to("appointments"))
        new_prescription_btn.clicked.connect(lambda: self.main_window.navigate_to("prescriptions"))
        
        for btn in [add_patient_btn, add_medicine_btn, new_appointment_btn, new_prescription_btn]:
            actions_layout.addWidget(btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        self.setLayout(layout)

    def _create_stat_card(self, title: str, value: str, color: str) -> QWidget:
        """Create a statistics card."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout()
        
        label = QLabel(title)
        label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        card.setMinimumWidth(180)
        return card

    def refresh(self):
        """Refresh dashboard data."""
        from models import Patient, Appointment, Medicine, Prescription
        from datetime import date
        
        self.stats['patients'].layout().itemAt(1).widget().setText(
            str(len(Patient.get_all())))
        self.stats['appointments'].layout().itemAt(1).widget().setText(
            str(len(Appointment.get_by_date(date.today().isoformat()))))
        self.stats['medicines'].layout().itemAt(1).widget().setText(
            str(len(Medicine.get_all())))
        self.stats['prescriptions'].layout().itemAt(1).widget().setText(
            str(len(Prescription.get_all())))