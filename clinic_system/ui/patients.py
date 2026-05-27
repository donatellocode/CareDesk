"""Patients management page."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit,
                             QDialog, QFormLayout, QSpinBox, QComboBox,
                             QTextEdit, QLabel, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from typing import List
from models import Patient, Visit, Appointment


class PatientsPage(QWidget):
    """Patients management interface."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.patients = []
        self.setup_ui()

    def setup_ui(self):
        """Setup patients page UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Patients")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ Add Patient")
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patients by name or phone...")
        self.search_input.setStyleSheet("""
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        """)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        clear_btn.clicked.connect(lambda: self.search_input.clear())
        search_layout.addWidget(clear_btn)
        
        layout.addLayout(search_layout)
        
        # Patients table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Gender", "Phone", "Actions"])
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
        """Refresh patient list."""
        self.load_patients(Patient.get_all())

    def load_patients(self, patients: List[Patient]):
        """Load patients into table."""
        self.patients = patients
        self.table.setRowCount(0)
        
        for patient in patients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(patient.id)))
            self.table.setItem(row, 1, QTableWidgetItem(patient.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(patient.age or "N/A")))
            self.table.setItem(row, 3, QTableWidgetItem(patient.gender or "N/A"))
            self.table.setItem(row, 4, QTableWidgetItem(patient.phone or "N/A"))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 10px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
            """)
            edit_btn.clicked.connect(lambda _, p=patient: self.show_edit_dialog(p))
            
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 10px;
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
            """)
            view_btn.clicked.connect(lambda _, p=patient: self.show_patient_details(p))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(view_btn)
            actions_widget.setLayout(actions_layout)
            
            self.table.setCellWidget(row, 5, actions_widget)

    def on_search(self, text: str):
        """Handle search input."""
        if len(text) >= 2:
            patients = Patient.search(text)
        else:
            patients = Patient.get_all()
        self.load_patients(patients)

    def show_add_dialog(self):
        """Show add patient dialog."""
        dialog = PatientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def show_edit_dialog(self, patient: Patient):
        """Show edit patient dialog."""
        dialog = PatientDialog(self, patient)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def show_patient_details(self, patient: Patient):
        """Show patient details dialog."""
        dialog = PatientDetailsDialog(self, patient)
        dialog.exec()


class PatientDialog(QDialog):
    """Dialog for adding/editing patients."""

    def __init__(self, parent, patient: Patient = None):
        super().__init__(parent)
        self.patient = patient
        self.setWindowTitle("Add Patient" if patient is None else "Edit Patient")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        if self.patient:
            self.name_input.setText(self.patient.name)
        
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 150)
        if self.patient and self.patient.age:
            self.age_input.setValue(self.patient.age)
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(["", "Male", "Female", "Other"])
        if self.patient and self.patient.gender:
            self.gender_input.setCurrentText(self.patient.gender)
        
        self.phone_input = QLineEdit()
        if self.patient:
            self.phone_input.setText(self.patient.phone)
        
        self.notes_input = QTextEdit()
        if self.patient:
            self.notes_input.setText(self.patient.notes)
        self.notes_input.setMaximumHeight(80)
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Age:", self.age_input)
        layout.addRow("Gender:", self.gender_input)
        layout.addRow("Phone:", self.phone_input)
        layout.addRow("Notes:", self.notes_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2980b9; }
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
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow("", btn_layout)
        self.setLayout(layout)

    def save(self):
        """Save patient."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Name is required!")
            return
        
        age = self.age_input.value() if self.age_input.value() > 0 else None
        gender = self.gender_input.currentText()
        phone = self.phone_input.text().strip()
        notes = self.notes_input.toPlainText().strip()
        
        if self.patient:
            self.patient.name = name
            self.patient.age = age
            self.patient.gender = gender
            self.patient.phone = phone
            self.patient.notes = notes
            self.patient.update()
        else:
            Patient.create(name, age, phone, gender, notes)
        
        self.accept()


class PatientDetailsDialog(QDialog):
    """Dialog showing patient details and history."""

    def __init__(self, parent, patient: Patient):
        super().__init__(parent)
        self.patient = patient
        self.setWindowTitle(f"Patient: {patient.name}")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        """Setup details UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Patient info
        info_label = QLabel(f"<b>Patient Details</b>")
        info_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(info_label)
        
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"<b>Name:</b> {self.patient.name}"))
        info_layout.addWidget(QLabel(f"<b>Age:</b> {self.patient.age or 'N/A'}"))
        info_layout.addWidget(QLabel(f"<b>Gender:</b> {self.patient.gender or 'N/A'}"))
        info_layout.addWidget(QLabel(f"<b>Phone:</b> {self.patient.phone or 'N/A'}"))
        if self.patient.notes:
            info_layout.addWidget(QLabel(f"<b>Notes:</b> {self.patient.notes}"))
        
        layout.addLayout(info_layout)
        
        # Visits history
        visits_label = QLabel("<b>Visit History</b>")
        visits_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(visits_label)
        
        visits = Visit.get_by_patient(self.patient.id)
        if visits:
            visits_table = QTableWidget()
            visits_table.setColumnCount(4)
            visits_table.setHorizontalHeaderLabels(["Date", "Diagnosis", "Notes", "Appointment"])
            visits_table.setRowCount(len(visits))
            
            for i, visit in enumerate(visits):
                visits_table.setItem(i, 0, QTableWidgetItem(visit.date))
                visits_table.setItem(i, 1, QTableWidgetItem(visit.diagnosis or ""))
                visits_table.setItem(i, 2, QTableWidgetItem(visit.notes or ""))
                appt = Appointment.get_by_id(visit.appointment_id) if visit.appointment_id else None
                visits_table.setItem(i, 3, QTableWidgetItem(
                    f"{appt.date} {appt.time}" if appt else "N/A"))
            
            visits_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            visits_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            layout.addWidget(visits_table)
        else:
            layout.addWidget(QLabel("No visits recorded."))
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)