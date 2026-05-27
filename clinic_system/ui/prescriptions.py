"""Prescriptions management page with smart medicine selection."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit,
                             QDialog, QFormLayout, QComboBox,
                             QLabel, QMessageBox, QHeaderView, QCheckBox,
                             QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt
from datetime import date
from typing import List, Optional
from models import Prescription, PrescriptionItem, Medicine, Patient, Visit, Appointment
from services.prescription_service import PrescriptionService


class PrescriptionsPage(QWidget):
    """Prescriptions management interface."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.prescriptions = []
        self.setup_ui()

    def setup_ui(self):
        """Setup prescriptions page UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Prescriptions")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        create_btn = QPushButton("📝 Create Prescription")
        create_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        create_btn.clicked.connect(self.show_create_dialog)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Search
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search prescriptions...")
        self.search_input.setStyleSheet("""
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        """)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("padding: 10px 20px; background-color: #3498db; color: white; border: none; border-radius: 5px;")
        refresh_btn.clicked.connect(self.refresh)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Prescriptions table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Patient", "Items", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
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
        """Refresh prescriptions list."""
        prescriptions = Prescription.get_all()
        prescriptions = sorted(prescriptions, key=lambda p: p.date or "", reverse=True)
        self.load_prescriptions(prescriptions)

    def load_prescriptions(self, prescriptions: List[Prescription]):
        """Load prescriptions into table."""
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
            
            # Count items
            items = PrescriptionItem.get_by_prescription(pres.id)
            self.table.setItem(row, 3, QTableWidgetItem(f"{len(items)} medicines"))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 10px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
            """)
            view_btn.clicked.connect(lambda _, p=pres: self.show_view_dialog(p))
            
            pdf_btn = QPushButton("PDF")
            pdf_btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 10px;
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
            """)
            pdf_btn.clicked.connect(lambda _, p=pres: self.generate_pdf(p))
            
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
            del_btn.clicked.connect(lambda _, p=pres: self.delete_prescription(p))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(pdf_btn)
            actions_layout.addWidget(del_btn)
            actions_widget.setLayout(actions_layout)
            
            self.table.setCellWidget(row, 4, actions_widget)

    def on_search(self, text: str):
        """Handle search input."""
        # Simple search - filter by patient name
        all_prescriptions = Prescription.get_all()
        if text:
            filtered = [p for p in all_prescriptions if text.lower() in (p.patient_name or "").lower()]
            self.load_prescriptions(filtered)
        else:
            self.refresh()

    def show_create_dialog(self):
        """Show create prescription dialog."""
        dialog = CreatePrescriptionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def show_view_dialog(self, prescription: Prescription):
        """Show prescription details."""
        dialog = ViewPrescriptionDialog(self, prescription)
        dialog.exec()

    def generate_pdf(self, prescription: Prescription):
        """Generate PDF for prescription."""
        from utils.pdf_generator import PDFGenerator
        from PyQt6.QtWidgets import QFileDialog
        
        # Get patient info
        patient = Patient.get_by_id(prescription.patient_id)
        
        # Get prescription items
        items = PrescriptionItem.get_by_prescription(prescription.id)
        item_data = []
        for item in items:
            item_data.append({
                'medicine_name': item.medicine_name or "",
                'dose': item.dose or "",
                'instructions': item.instructions or ""
            })
        
        # Show save dialog
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
        """Delete a prescription."""
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
        """Setup dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Patient selection
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
        
        # Medicine selection
        medicine_group = QGroupBox("Medicines (Select from Database)")
        medicine_layout = QVBoxLayout()
        
        # Search medicines
        search_layout = QHBoxLayout()
        self.medicine_search = QLineEdit()
        self.medicine_search.setPlaceholderText("Search medicines...")
        self.medicine_search.textChanged.connect(self.filter_medicines)
        search_layout.addWidget(self.medicine_search)
        medicine_layout.addLayout(search_layout)
        
        # Medicine list (table)
        self.medicine_table = QTableWidget()
        self.medicine_table.setColumnCount(5)
        self.medicine_table.setHorizontalHeaderLabels(["", "Name", "Category", "Default Dose", "Instructions"])
        self.medicine_table.setColumnWidth(0, 30)  # Checkbox column
        self.medicine_table.setColumnWidth(1, 150)
        self.medicine_table.setColumnWidth(2, 100)
        self.medicine_table.setColumnWidth(3, 120)
        self.medicine_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.medicine_table.setMinimumHeight(200)
        self.load_medicines(Medicine.get_all())
        medicine_layout.addWidget(self.medicine_table)
        
        medicine_group.setLayout(medicine_layout)
        layout.addWidget(medicine_group)
        
        # Selected medicines
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
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Prescription")
        create_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 30px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        create_btn.clicked.connect(self.create_prescription)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 30px;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_patients(self):
        """Load patients into combo."""
        patients = Patient.get_all()
        self.patient_combo.clear()
        self.patient_combo.addItem("", None)
        for p in patients:
            self.patient_combo.addItem(f"{p.name} ({p.phone})", p.id)

    def load_medicines(self, medicines: List[Medicine]):
        """Load medicines into selection table."""
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
        """Filter medicines by search text."""
        if len(text) >= 2:
            medicines = Medicine.search(text)
        else:
            medicines = Medicine.get_all()
        self.load_medicines(medicines)

    def on_medicine_toggled(self, medicine: Medicine, state: int):
        """Handle medicine selection."""
        if state == Qt.CheckState.Checked.value:
            if medicine not in self.selected_medicines:
                self.selected_medicines.append(medicine)
                self.update_selected_table()
        else:
            if medicine in self.selected_medicines:
                self.selected_medicines.remove(medicine)
                self.update_selected_table()

    def update_selected_table(self):
        """Update selected medicines table."""
        self.selected_table.setRowCount(0)
        
        for med in self.selected_medicines:
            row = self.selected_table.rowCount()
            self.selected_table.insertRow(row)
            
            self.selected_table.setItem(row, 0, QTableWidgetItem(med.name))
            self.selected_table.setItem(row, 1, QTableWidgetItem(med.default_dose or ""))
            self.selected_table.setItem(row, 2, QTableWidgetItem(med.instructions or ""))
            
            remove_btn = QPushButton("✕")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 8px;
                }
            """)
            remove_btn.clicked.connect(lambda _, m=med: self.remove_medicine(m))
            self.selected_table.setCellWidget(row, 3, remove_btn)

    def remove_medicine(self, medicine: Medicine):
        """Remove medicine from selection."""
        if medicine in self.selected_medicines:
            self.selected_medicines.remove(medicine)
            self.update_selected_table()
            
            # Uncheck in medicine table
            for row in range(self.medicine_table.rowCount()):
                checkbox = self.medicine_table.cellWidget(row, 0)
                if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                    # Find the medicine for this row
                    name_item = self.medicine_table.item(row, 1)
                    if name_item and name_item.text() == medicine.name:
                        checkbox.setChecked(False)
                        break

    def add_new_patient(self):
        """Add a new patient."""
        from .patients import PatientDialog
        dialog = PatientDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_patients()

    def create_prescription(self):
        """Create the prescription."""
        patient_id = self.patient_combo.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Error", "Please select a patient!")
            return
        
        if not self.selected_medicines:
            QMessageBox.warning(self, "Error", "Please select at least one medicine!")
            return
        
        try:
            # Create prescription
            prescription = PrescriptionService.create_prescription(
                patient_id=patient_id,
                date=date.today().isoformat()
            )
            
            # Add medicines
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
    """Dialog for viewing prescription details."""

    def __init__(self, parent, prescription: Prescription):
        super().__init__(parent)
        self.prescription = prescription
        self.setWindowTitle(f"Prescription #{prescription.id}")
        self.setMinimumSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Prescription info
        patient = Patient.get_by_id(self.prescription.patient_id)
        
        info_label = QLabel(f"""
            <b>Patient:</b> {patient.name if patient else 'Unknown'}<br>
            <b>Date:</b> {self.prescription.date}<br>
            <b>ID:</b> #{self.prescription.id}
        """)
        info_label.setStyleSheet("padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # Medicines list
        items_label = QLabel("<b>Prescribed Medicines:</b>")
        items_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(items_label)
        
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