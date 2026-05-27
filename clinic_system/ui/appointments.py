"""Appointments management page."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit,
                             QDialog, QFormLayout, QComboBox,
                             QLabel, QMessageBox, QHeaderView, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from datetime import date, timedelta
from typing import List, Optional
from models import Appointment, Patient


class AppointmentsPage(QWidget):
    """Appointments management interface."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_date = date.today()
        self.appointments = []
        self.setup_ui()

    def setup_ui(self):
        """Setup appointments page UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Appointments")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ New Appointment")
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Date navigation
        date_nav_layout = QHBoxLayout()
        date_nav_layout.setSpacing(10)
        
        prev_btn = QPushButton("◀ Previous")
        prev_btn.setStyleSheet("padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 5px;")
        prev_btn.clicked.connect(self.previous_day)
        
        self.date_label = QLabel(self.current_date.strftime("%A, %B %d, %Y"))
        self.date_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 0 20px;")
        
        next_btn = QPushButton("Next ▶")
        next_btn.setStyleSheet("padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 5px;")
        next_btn.clicked.connect(self.next_day)
        
        today_btn = QPushButton("Today")
        today_btn.setStyleSheet("padding: 8px 15px; background-color: #9b59b6; color: white; border: none; border-radius: 5px;")
        today_btn.clicked.connect(self.go_to_today)
        
        date_nav_layout.addWidget(prev_btn)
        date_nav_layout.addWidget(self.date_label)
        date_nav_layout.addWidget(next_btn)
        date_nav_layout.addWidget(today_btn)
        
        layout.addLayout(date_nav_layout)
        
        # Appointments table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Patient", "Status", "Phone", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 10px;
                font-weight: bold;
            }
        """)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def refresh(self):
        """Refresh appointments list."""
        self.date_label.setText(self.current_date.strftime("%A, %B %d, %Y"))
        appointments = Appointment.get_by_date(self.current_date.isoformat())
        self.load_appointments(appointments)

    def load_appointments(self, appointments: List[Appointment]):
        """Load appointments into table."""
        self.appointments = appointments
        self.table.setRowCount(0)
        
        if not appointments:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 5)
            empty_item = QTableWidgetItem("No appointments for this day. Click 'New Appointment' to create one.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            return
        
        for appt in appointments:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(appt.time))
            self.table.setItem(row, 1, QTableWidgetItem(appt.patient_name or ""))
            
            # Status with color
            status_item = QTableWidgetItem(appt.status.capitalize())
            if appt.status == "waiting":
                status_item.setBackground(Qt.GlobalColor.yellow)
            elif appt.status == "done":
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            elif appt.status == "cancelled":
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            self.table.setItem(row, 2, status_item)
            
            patient = Patient.get_by_id(appt.patient_id)
            self.table.setItem(row, 3, QTableWidgetItem(patient.phone if patient else ""))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            # Status change dropdown
            status_combo = QComboBox()
            status_combo.addItems(["waiting", "done", "cancelled"])
            status_combo.setCurrentText(appt.status)
            status_combo.currentTextChanged.connect(
                lambda s, a=appt: self.change_status(a, s)
            )
            status_combo.setStyleSheet("padding: 5px;")
            
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 10px;
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
            """)
            del_btn.clicked.connect(lambda _, a=appt: self.delete_appointment(a))
            
            actions_layout.addWidget(status_combo)
            actions_layout.addWidget(del_btn)
            actions_widget.setLayout(actions_layout)
            
            self.table.setCellWidget(row, 4, actions_widget)

    def change_status(self, appointment: Appointment, status: str):
        """Change appointment status."""
        appointment.update_status(status)
        self.refresh()

    def previous_day(self):
        """Go to previous day."""
        self.current_date -= timedelta(days=1)
        self.refresh()

    def next_day(self):
        """Go to next day."""
        self.current_date += timedelta(days=1)
        self.refresh()

    def go_to_today(self):
        """Go to today."""
        self.current_date = date.today()
        self.refresh()

    def show_add_dialog(self):
        """Show add appointment dialog."""
        dialog = AppointmentDialog(self, self.current_date)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def delete_appointment(self, appointment: Appointment):
        """Delete an appointment."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete appointment for {appointment.patient_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            appointment.delete()
            self.refresh()


class AppointmentDialog(QDialog):
    """Dialog for creating appointments."""

    def __init__(self, parent, default_date: date = None):
        super().__init__(parent)
        self.default_date = default_date or date.today()
        self.setWindowTitle("New Appointment")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Patient selection
        patient_layout = QHBoxLayout()
        self.patient_combo = QComboBox()
        self.patient_combo.setEditable(True)
        self.patient_combo.setMinimumWidth(250)
        self.load_patients()
        patient_layout.addWidget(self.patient_combo)
        
        add_new_btn = QPushButton("+ New Patient")
        add_new_btn.setStyleSheet("padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 5px;")
        add_new_btn.clicked.connect(self.add_new_patient)
        patient_layout.addWidget(add_new_btn)
        
        layout.addRow("Patient *:", patient_layout)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate(self.default_date.year, self.default_date.month, self.default_date.day))
        self.date_input.setCalendarPopup(True)
        layout.addRow("Date *:", self.date_input)
        
        # Time
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("e.g., 09:00 AM")
        layout.addRow("Time *:", self.time_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Create Appointment")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        save_btn.clicked.connect(self.save)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow("", btn_layout)
        self.setLayout(layout)

    def load_patients(self):
        """Load patients into combo."""
        patients = Patient.get_all()
        self.patient_combo.clear()
        self.patient_combo.addItem("", None)
        for p in patients:
            self.patient_combo.addItem(f"{p.name} ({p.phone})", p.id)

    def add_new_patient(self):
        """Add a new patient."""
        from .patients import PatientDialog
        dialog = PatientDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_patients()

    def save(self):
        """Save appointment."""
        patient_id = self.patient_combo.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Error", "Please select a patient!")
            return
        
        time = self.time_input.text().strip()
        if not time:
            QMessageBox.warning(self, "Error", "Time is required!")
            return
        
        appt_date = self.date_input.date().toString("yyyy-MM-dd")
        
        try:
            Appointment.create(patient_id, appt_date, time)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create appointment: {e}")