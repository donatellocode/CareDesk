"""Main window with sidebar navigation - All UI pages consolidated."""

# All page classes are defined in this single file to avoid import issues
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QStackedWidget, QLabel, QLineEdit, QMessageBox,
                             QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                             QSpinBox, QComboBox, QTextEdit, QHeaderView, QDateEdit,
                             QGroupBox, QCheckBox, QFileDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon
from datetime import date, timedelta
from typing import List, Optional

from models import Patient, Medicine, Appointment, Visit, Prescription, PrescriptionItem


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
        
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
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
        
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        buttons = [
            ("➕ Add Patient", "patients"),
            ("💊 Add Medicine", "medicines"),
            ("📅 New Appointment", "appointments"),
            ("📝 New Prescription", "prescriptions"),
        ]
        
        for text, page in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 20px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #2980b9; }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, p=page: self.main_window.navigate_to(p))
            actions_layout.addWidget(btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        self.setLayout(layout)

    def _create_stat_card(self, title: str, value: str, color: str) -> QWidget:
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
        self.stats['patients'].layout().itemAt(1).widget().setText(str(len(Patient.get_all())))
        self.stats['appointments'].layout().itemAt(1).widget().setText(
            str(len(Appointment.get_by_date(date.today().isoformat()))))
        self.stats['medicines'].layout().itemAt(1).widget().setText(str(len(Medicine.get_all())))
        self.stats['prescriptions'].layout().itemAt(1).widget().setText(str(len(Prescription.get_all())))


class PatientsPage(QWidget):
    """Patients management interface."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.patients = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
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
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patients by name or phone...")
        self.search_input.setStyleSheet("padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px;")
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
        """)
        clear_btn.clicked.connect(lambda: self.search_input.clear())
        search_layout.addWidget(clear_btn)
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Gender", "Phone", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; border-radius: 5px; }
            QHeaderView::section { background-color: #ecf0f1; padding: 10px; font-weight: bold; }
        """)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self):
        self.load_patients(Patient.get_all())

    def load_patients(self, patients: List[Patient]):
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
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("padding: 5px 10px; background-color: #3498db; color: white; border: none; border-radius: 3px;")
            edit_btn.clicked.connect(lambda _, p=patient: self.show_edit_dialog(p))
            
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("padding: 5px 10px; background-color: #2ecc71; color: white; border: none; border-radius: 3px;")
            view_btn.clicked.connect(lambda _, p=patient: self.show_patient_details(p))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(view_btn)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 5, actions_widget)

    def on_search(self, text: str):
        if len(text) >= 2:
            patients = Patient.search(text)
        else:
            patients = Patient.get_all()
        self.load_patients(patients)

    def show_add_dialog(self):
        dialog = PatientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def show_edit_dialog(self, patient: Patient):
        dialog = PatientDialog(self, patient)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def show_patient_details(self, patient: Patient):
        dialog = PatientDetailsDialog(self, patient)
        dialog.exec()


class PatientDialog(QDialog):
    def __init__(self, parent, patient: Patient = None):
        super().__init__(parent)
        self.patient = patient
        self.setWindowTitle("Add Patient" if patient is None else "Edit Patient")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
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
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("padding: 10px 30px; background-color: #3498db; color: white; border: none; border-radius: 5px;")
        save_btn.clicked.connect(self.save)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("padding: 10px 30px; background-color: #95a5a6; color: white; border: none; border-radius: 5px;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow("", btn_layout)
        self.setLayout(layout)

    def save(self):
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
    def __init__(self, parent, patient: Patient):
        super().__init__(parent)
        self.patient = patient
        self.setWindowTitle(f"Patient: {patient.name}")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        layout.addWidget(QLabel(f"<b>Patient Details</b>"))
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"<b>Name:</b> {self.patient.name}"))
        info_layout.addWidget(QLabel(f"<b>Age:</b> {self.patient.age or 'N/A'}"))
        info_layout.addWidget(QLabel(f"<b>Gender:</b> {self.patient.gender or 'N/A'}"))
        info_layout.addWidget(QLabel(f"<b>Phone:</b> {self.patient.phone or 'N/A'}"))
        if self.patient.notes:
            info_layout.addWidget(QLabel(f"<b>Notes:</b> {self.patient.notes}"))
        layout.addLayout(info_layout)
        
        layout.addWidget(QLabel("<b>Visit History</b>"))
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
                visits_table.setItem(i, 3, QTableWidgetItem(f"{appt.date} {appt.time}" if appt else "N/A"))
            
            visits_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            visits_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            layout.addWidget(visits_table)
        else:
            layout.addWidget(QLabel("No visits recorded."))
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("padding: 10px 30px; background-color: #95a5a6; color: white; border: none; border-radius: 5px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)


class MedicinesPage(QWidget):
    """Medicines database management interface."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.medicines = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        title = QLabel("Medicine Database")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ Add Medicine")
        add_btn.setStyleSheet("padding: 10px 20px; background-color: #9b59b6; color: white; border: none; border-radius: 5px; font-size: 14px;")
        add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        desc = QLabel("💊 Add medicines to the database. During prescription, select medicines to auto-fill dose and instructions.")
        desc.setStyleSheet("color: #7f8c8d; font-size: 13px; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(desc)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search medicines by name or category...")
        self.search_input.setStyleSheet("padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px;")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("padding: 10px 20px; background-color: #95a5a6; color: white; border: none; border-radius: 5px;")
        clear_btn.clicked.connect(lambda: self.search_input.clear())
        search_layout.addWidget(clear_btn)
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Default Dose", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; border-radius: 5px; }
            QHeaderView::section { background-color: #ecf0f1; padding: 10px; font-weight: bold; }
        """)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self):
        self.load_medicines(Medicine.get_all())

    def load_medicines(self, medicines: List[Medicine]):
        self.medicines = medicines
        self.table.setRowCount(0)
        
        for medicine in medicines:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(medicine.id)))
            self.table.setItem(row, 1, QTableWidgetItem(medicine.name))
            self.table.setItem(row, 2, QTableWidgetItem(medicine.category or ""))
            self.table.setItem(row, 3, QTableWidgetItem(medicine.default_dose or ""))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("padding: 5px 10px; background-color: #3498db; color: white; border: none; border-radius: 3px;")
            edit_btn.clicked.connect(lambda _, m=medicine: self.show_edit_dialog(m))
            
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("padding: 5px 10px; background-color: #e74c3c; color: white; border: none; border-radius: 3px;")
            del_btn.clicked.connect(lambda _, m=medicine: self.delete_medicine(m))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(del_btn)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)

    def on_search(self, text: str):
        if len(text) >= 2:
            medicines = Medicine.search(text)
        else:
            medicines = Medicine.get_all()
        self.load_medicines(medicines)

    def show_add_dialog(self):
        dialog = MedicineDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def show_edit_dialog(self, medicine: Medicine):
        dialog = MedicineDialog(self, medicine)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def delete_medicine(self, medicine: Medicine):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete medicine '{medicine.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            medicine.delete()
            self.refresh()


class MedicineDialog(QDialog):
    def __init__(self, parent, medicine: Medicine = None):
        super().__init__(parent)
        self.medicine = medicine
        self.setWindowTitle("Add Medicine" if medicine is None else "Edit Medicine")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        if self.medicine:
            self.name_input.setText(self.medicine.name)
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems([
            "", "Analgesic", "Antibiotic", "Antihistamine", "Antiviral",
            "Cardiovascular", "Diabetes", "Gastrointestinal", "Respiratory",
            "Dermatological", "Other"
        ])
        if self.medicine and self.medicine.category:
            self.category_input.setCurrentText(self.medicine.category)
        
        self.dose_input = QLineEdit()
        if self.medicine:
            self.dose_input.setText(self.medicine.default_dose)
        self.dose_input.setPlaceholderText("e.g., 500mg, 1 tablet, 5ml")
        
        self.instructions_input = QTextEdit()
        if self.medicine:
            self.instructions_input.setText(self.medicine.instructions)
        self.instructions_input.setPlaceholderText("e.g., Take 3 times daily after meals")
        self.instructions_input.setMaximumHeight(80)
        
        layout.addRow("Name *:", self.name_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Default Dose:", self.dose_input)
        layout.addRow("Instructions:", self.instructions_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("padding: 10px 30px; background-color: #9b59b6; color: white; border: none; border-radius: 5px;")
        save_btn.clicked.connect(self.save)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("padding: 10px 30px; background-color: #95a5a6; color: white; border: none; border-radius: 5px;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow("", btn_layout)
        self.setLayout(layout)

    def save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Medicine name is required!")
            return
        
        category = self.category_input.currentText().strip()
        default_dose = self.dose_input.text().strip()
        instructions = self.instructions_input.toPlainText().strip()
        
        if self.medicine:
            self.medicine.name = name
            self.medicine.category = category
            self.medicine.default_dose = default_dose
            self.medicine.instructions = instructions
            self.medicine.update()
        else:
            try:
                Medicine.create(name, category, default_dose, instructions)
            except Exception as e:
                QMessageBox.warning(self, "Error", "Medicine already exists or invalid data!")
                return
        
        self.accept()


class AppointmentsPage(QWidget):
    """Appointments management interface."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_date = date.today()
        self.appointments = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        title = QLabel("Appointments")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ New Appointment")
        add_btn.setStyleSheet("padding: 10px 20px; background-color: #2ecc71; color: white; border: none; border-radius: 5px; font-size: 14px;")
        add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
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
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Patient", "Status", "Phone", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; border-radius: 5px; }
            QHeaderView::section { background-color: #ecf0f1; padding: 10px; font-weight: bold; }
        """)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self):
        self.date_label.setText(self.current_date.strftime("%A, %B %d, %Y"))
        appointments = Appointment.get_by_date(self.current_date.isoformat())
        self.load_appointments(appointments)

    def load_appointments(self, appointments: List[Appointment]):
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
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            status_combo = QComboBox()
            status_combo.addItems(["waiting", "done", "cancelled"])
            status_combo.setCurrentText(appt.status)
            status_combo.currentTextChanged.connect(lambda s, a=appt: self.change_status(a, s))
            status_combo.setStyleSheet("padding: 5px;")
            
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("padding: 5px 10px; background-color: #e74c3c; color: white; border: none; border-radius: 3px;")
            del_btn.clicked.connect(lambda _, a=appt: self.delete_appointment(a))
            
            actions_layout.addWidget(status_combo)
            actions_layout.addWidget(del_btn)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)

    def change_status(self, appointment: Appointment, status: str):
        appointment.update_status(status)
        self.refresh()

    def previous_day(self):
        self.current_date -= timedelta(days=1)
        self.refresh()

    def next_day(self):
        self.current_date += timedelta(days=1)
        self.refresh()

    def go_to_today(self):
        self.current_date = date.today()
        self.refresh()

    def show_add_dialog(self):
        dialog = AppointmentDialog(self, self.current_date)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def delete_appointment(self, appointment: Appointment):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete appointment for {appointment.patient_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            appointment.delete()
            self.refresh()


class AppointmentDialog(QDialog):
    def __init__(self, parent, default_date: date = None):
        super().__init__(parent)
        self.default_date = default_date or date.today()
        self.setWindowTitle("New Appointment")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setSpacing(15)
        
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
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate(self.default_date.year, self.default_date.month, self.default_date.day))
        self.date_input.setCalendarPopup(True)
        layout.addRow("Date *:", self.date_input)
        
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("e.g., 09:00 AM")
        layout.addRow("Time *:", self.time_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Create Appointment")
        save_btn.setStyleSheet("padding: 10px 30px; background-color: #2ecc71; color: white; border: none; border-radius: 5px;")
        save_btn.clicked.connect(self.save)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("padding: 10px 30px; background-color: #95a5a6; color: white; border: none; border-radius: 5px;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow("", btn_layout)
        self.setLayout(layout)

    def load_patients(self):
        patients = Patient.get_all()
        self.patient_combo.clear()
        self.patient_combo.addItem("", None)
        for p in patients:
            self.patient_combo.addItem(f"{p.name} ({p.phone})", p.id)

    def add_new_patient(self):
        dialog = PatientDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_patients()

    def save(self):
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


class PrescriptionsPage(QWidget):
    """Prescriptions management interface."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.prescriptions = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        title = QLabel("Prescriptions")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        create_btn = QPushButton("📝 Create Prescription")
        create_btn.setStyleSheet("padding: 10px 20px; background-color: #e74c3c; color: white; border: none; border-radius: 5px; font-size: 14px;")
        create_btn.clicked.connect(self.show_create_dialog)
        header_layout.addWidget(create_btn)
        layout.addLayout(header_layout)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search prescriptions...")
        self.search_input.setStyleSheet("padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px;")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("padding: 10px 20px; background-color: #3498db; color: white; border: none; border-radius: 5px;")
        refresh_btn.clicked.connect(self.refresh)
        search_layout.addWidget(refresh_btn)
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Patient", "Items", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; border-radius: 5px; }
            QHeaderView::section { background-color: #ecf0f1; padding: 10px; font-weight: bold; }
        """)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self):
        prescriptions = Prescription.get_all()
        prescriptions = sorted(prescriptions, key=lambda p: p.date or "", reverse=True)
        self.load_prescriptions(prescriptions)

    def load_prescriptions(self, prescriptions: List[Prescription]):
        self.prescriptions = prescriptions
        self.table.setRowCount(0)
        
        if not prescriptions:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 5)
            empty_item = QTableWidgetItem("No prescriptions yet. Click 'Create Prescription' to create one.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            return
        
        for pres in prescriptions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(pres.id)))
            self.table.setItem(row, 1, QTableWidgetItem(pres.date))
            self.table.setItem(row, 2, QTableWidgetItem(pres.patient_name or ""))
            
            items = PrescriptionItem.get_by_prescription(pres.id)
            self.table.setItem(row, 3, QTableWidgetItem(f"{len(items)} medicines"))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("padding: 5px 10px; background-color: #3498db; color: white; border: none; border-radius: 3px;")
            view_btn.clicked.connect(lambda _, p=pres: self.show_view_dialog(p))
            
            pdf_btn = QPushButton("PDF")
            pdf_btn.setStyleSheet("padding: 5px 10px; background-color: #2ecc71; color: white; border: none; border-radius: 3px;")
            pdf_btn.clicked.connect(lambda _, p=pres: self.generate_pdf(p))
            
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("padding: 5px 10px; background-color: #e74c3c; color: white; border: none; border-radius: 3px;")
            del_btn.clicked.connect(lambda _, p=pres: self.delete_prescription(p))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(pdf_btn)
            actions_layout.addWidget(del_btn)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)

    def on_search(self, text: str):
        all_prescriptions = Prescription.get_all()
        if text:
            filtered = [p for p in all_prescriptions if text.lower() in (p.patient_name or "").lower()]
            self.load_prescriptions(filtered)
        else:
            self.refresh()

    def show_create_dialog(self):
        dialog = CreatePrescriptionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def show_view_dialog(self, prescription: Prescription):
        dialog = ViewPrescriptionDialog(self, prescription)
        dialog.exec()

    def generate_pdf(self, prescription: Prescription):
        from utils.pdf_generator import PDFGenerator
        
        patient = Patient.get_by_id(prescription.patient_id)
        items = PrescriptionItem.get_by_prescription(prescription.id)
        item_data = []
        for item in items:
            item_data.append({
                'medicine_name': item.medicine_name or "",
                'dose': item.dose or "",
                'instructions': item.instructions or ""
            })
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Prescription PDF",
            f"prescription_{prescription.id}_{prescription.date}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if filename:
            generator = PDFGenerator()
            success = generator.generate_prescription(
                patient_name=patient.name if patient else "Unknown",
                patient_age=patient.age if patient else None,
                patient_gender=patient.gender if patient else "",
                date=prescription.date,
                items=item_data,
                output_path=filename
            )
            
            if success:
                QMessageBox.information(self, "Success", f"PDF saved to {filename}")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate PDF")

    def delete_prescription(self, prescription: Prescription):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete prescription #{prescription.id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            prescription.delete()
            self.refresh()


class CreatePrescriptionDialog(QDialog):
    """Dialog for creating prescriptions with smart medicine selection."""

    def __init__(self, parent):
        super().__init__(parent)
        self.prescription = None
        self.selected_medicines = []
        self.setWindowTitle("Create Prescription")
        self.setMinimumSize(700, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        patient_group = QGroupBox("Patient Information")
        patient_layout = QHBoxLayout()
        
        self.patient_combo = QComboBox()
        self.patient_combo.setEditable(True)
        self.patient_combo.setMinimumWidth(300)
        self.load_patients()
        patient_layout.addWidget(QLabel("Patient:"))
        patient_layout.addWidget(self.patient_combo)
        
        add_patient_btn = QPushButton("+ New Patient")
        add_patient_btn.setStyleSheet("padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 5px;")
        add_patient_btn.clicked.connect(self.add_new_patient)
        patient_layout.addWidget(add_patient_btn)
        
        patient_group.setLayout(patient_layout)
        layout.addWidget(patient_group)
        
        medicine_group = QGroupBox("Medicines (Select from Database)")
        medicine_layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        self.medicine_search = QLineEdit()
        self.medicine_search.setPlaceholderText("Search medicines...")
        self.medicine_search.textChanged.connect(self.filter_medicines)
        search_layout.addWidget(self.medicine_search)
        medicine_layout.addLayout(search_layout)
        
        self.medicine_table = QTableWidget()
        self.medicine_table.setColumnCount(5)
        self.medicine_table.setHorizontalHeaderLabels(["", "Name", "Category", "Default Dose", "Instructions"])
        self.medicine_table.setColumnWidth(0, 30)
        self.medicine_table.setColumnWidth(1, 150)
        self.medicine_table.setColumnWidth(2, 100)
        self.medicine_table.setColumnWidth(3, 120)
        self.medicine_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.medicine_table.setMinimumHeight(200)
        self.load_medicines(Medicine.get_all())
        medicine_layout.addWidget(self.medicine_table)
        
        medicine_group.setLayout(medicine_layout)
        layout.addWidget(medicine_group)
        
        selected_group = QGroupBox("Selected Medicines")
        selected_layout = QVBoxLayout()
        
        self.selected_table = QTableWidget()
        self.selected_table.setColumnCount(4)
        self.selected_table.setHorizontalHeaderLabels(["Medicine", "Dose", "Instructions", "Remove"])
        self.selected_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.selected_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.selected_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.selected_table.setMinimumHeight(120)
        selected_layout.addWidget(self.selected_table)
        
        selected_group.setLayout(selected_layout)
        layout.addWidget(selected_group)
        
        btn_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Prescription")
        create_btn.setStyleSheet("padding: 12px 30px; background-color: #e74c3c; color: white; border: none; border-radius: 5px; font-size: 14px;")
        create_btn.clicked.connect(self.create_prescription)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("padding: 12px 30px; background-color: #95a5a6; color: white; border: none; border-radius: 5px;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_patients(self):
        patients = Patient.get_all()
        self.patient_combo.clear()
        self.patient_combo.addItem("", None)
        for p in patients:
            self.patient_combo.addItem(f"{p.name} ({p.phone})", p.id)

    def load_medicines(self, medicines: List[Medicine]):
        self.medicine_table.setRowCount(0)
        
        if not medicines:
            self.medicine_table.setRowCount(1)
            self.medicine_table.setSpan(0, 0, 1, 5)
            empty_item = QTableWidgetItem("No medicines in database. Add medicines first!")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.medicine_table.setItem(0, 0, empty_item)
            return
        
        for med in medicines:
            row = self.medicine_table.rowCount()
            self.medicine_table.insertRow(row)
            
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, m=med: self.on_medicine_toggled(m, state))
            self.medicine_table.setCellWidget(row, 0, checkbox)
            
            self.medicine_table.setItem(row, 1, QTableWidgetItem(med.name))
            self.medicine_table.setItem(row, 2, QTableWidgetItem(med.category or ""))
            self.medicine_table.setItem(row, 3, QTableWidgetItem(med.default_dose or ""))
            self.medicine_table.setItem(row, 4, QTableWidgetItem(med.instructions or ""))

    def filter_medicines(self, text: str):
        if len(text) >= 2:
            medicines = Medicine.search(text)
        else:
            medicines = Medicine.get_all()
        self.load_medicines(medicines)

    def on_medicine_toggled(self, medicine: Medicine, state: int):
        if state == Qt.CheckState.Checked.value:
            if medicine not in self.selected_medicines:
                self.selected_medicines.append(medicine)
                self.update_selected_table()
        else:
            if medicine in self.selected_medicines:
                self.selected_medicines.remove(medicine)
                self.update_selected_table()

    def update_selected_table(self):
        self.selected_table.setRowCount(0)
        
        for med in self.selected_medicines:
            row = self.selected_table.rowCount()
            self.selected_table.insertRow(row)
            
            self.selected_table.setItem(row, 0, QTableWidgetItem(med.name))
            self.selected_table.setItem(row, 1, QTableWidgetItem(med.default_dose or ""))
            self.selected_table.setItem(row, 2, QTableWidgetItem(med.instructions or ""))
            
            remove_btn = QPushButton("✕")
            remove_btn.setStyleSheet("background-color: #e74c3c; color: white; border: none; border-radius: 3px; padding: 3px 8px;")
            remove_btn.clicked.connect(lambda _, m=med: self.remove_medicine(m))
            self.selected_table.setCellWidget(row, 3, remove_btn)

    def remove_medicine(self, medicine: Medicine):
        if medicine in self.selected_medicines:
            self.selected_medicines.remove(medicine)
            self.update_selected_table()
            
            for row in range(self.medicine_table.rowCount()):
                checkbox = self.medicine_table.cellWidget(row, 0)
                if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                    name_item = self.medicine_table.item(row, 1)
                    if name_item and name_item.text() == medicine.name:
                        checkbox.setChecked(False)
                        break

    def add_new_patient(self):
        dialog = PatientDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_patients()

    def create_prescription(self):
        patient_id = self.patient_combo.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Error", "Please select a patient!")
            return
        
        if not self.selected_medicines:
            QMessageBox.warning(self, "Error", "Please select at least one medicine!")
            return
        
        try:
            prescription = Prescription.create(patient_id, date.today().isoformat())
            
            for med in self.selected_medicines:
                prescription.add_item(
                    medicine_id=med.id,
                    dose=med.default_dose,
                    instructions=med.instructions
                )
            
            self.prescription = prescription
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create prescription: {e}")


class ViewPrescriptionDialog(QDialog):
    def __init__(self, parent, prescription: Prescription):
        super().__init__(parent)
        self.prescription = prescription
        self.setWindowTitle(f"Prescription #{prescription.id}")
        self.setMinimumSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        patient = Patient.get_by_id(self.prescription.patient_id)
        
        info_label = QLabel(f"""
            <b>Patient:</b> {patient.name if patient else 'Unknown'}<br>
            <b>Date:</b> {self.prescription.date}<br>
            <b>ID:</b> #{self.prescription.id}
        """)
        info_label.setStyleSheet("padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(info_label)
        
        layout.addWidget(QLabel("<b>Prescribed Medicines:</b>"))
        
        items = PrescriptionItem.get_by_prescription(self.prescription.id)
        if items:
            items_table = QTableWidget()
            items_table.setColumnCount(4)
            items_table.setHorizontalHeaderLabels(["Medicine", "Dose", "Instructions", ""])
            items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            items_table.setRowCount(len(items))
            
            for i, item in enumerate(items):
                items_table.setItem(i, 0, QTableWidgetItem(item.medicine_name or ""))
                items_table.setItem(i, 1, QTableWidgetItem(item.dose or ""))
                items_table.setItem(i, 2, QTableWidgetItem(item.instructions or ""))
                items_table.setItem(i, 3, QTableWidgetItem(""))
            
            layout.addWidget(items_table)
        else:
            layout.addWidget(QLabel("No medicines in this prescription."))
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("padding: 10px 30px; background-color: #95a5a6; color: white; border: none; border-radius: 5px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


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
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)
        
        self.stacked_widget.addWidget(DashboardPage(self))
        self.stacked_widget.addWidget(PatientsPage(self))
        self.stacked_widget.addWidget(AppointmentsPage(self))
        self.stacked_widget.addWidget(MedicinesPage(self))
        self.stacked_widget.addWidget(PrescriptionsPage(self))
        
        self.window.setLayout(main_layout)
        
        self.navigate_to("dashboard")

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #2c3e50;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
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
        page_map = {
            "dashboard": 0,
            "patients": 1,
            "appointments": 2,
            "medicines": 3,
            "prescriptions": 4,
        }
        
        if page_id in page_map:
            for btn in self.sidebar_buttons.values():
                btn.setChecked(False)
            
            if page_id in self.sidebar_buttons:
                self.sidebar_buttons[page_id].setChecked(True)
            
            self.stacked_widget.setCurrentIndex(page_map[page_id])
            self.current_page = page_id
            
            widget = self.stacked_widget.currentWidget()
            if hasattr(widget, 'refresh'):
                widget.refresh()

    def show_message(self, title: str, message: str, 
                    icon: QMessageBox.Icon = QMessageBox.Icon.Information):
        msg = QMessageBox(self.window)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    def show_error(self, title: str, message: str):
        self.show_message(title, message, QMessageBox.Icon.Critical)