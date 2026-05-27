"""Medicines database management page."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit,
                             QDialog, QFormLayout, QComboBox,
                             QTextEdit, QLabel, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from typing import List
from models import Medicine


class MedicinesPage(QWidget):
    """Medicines database management interface."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.medicines = []
        self.setup_ui()

    def setup_ui(self):
        """Setup medicines page UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Medicine Database")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ Add Medicine")
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("💊 Add medicines to the database. During prescription, select medicines to auto-fill dose and instructions.")
        desc.setStyleSheet("color: #7f8c8d; font-size: 13px; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(desc)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search medicines by name or category...")
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
        
        # Medicines table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Default Dose", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
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
        """Refresh medicines list."""
        self.load_medicines(Medicine.get_all())

    def load_medicines(self, medicines: List[Medicine]):
        """Load medicines into table."""
        self.medicines = medicines
        self.table.setRowCount(0)
        
        for medicine in medicines:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(medicine.id)))
            self.table.setItem(row, 1, QTableWidgetItem(medicine.name))
            self.table.setItem(row, 2, QTableWidgetItem(medicine.category or ""))
            self.table.setItem(row, 3, QTableWidgetItem(medicine.default_dose or ""))
            
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
            edit_btn.clicked.connect(lambda _, m=medicine: self.show_edit_dialog(m))
            
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
            del_btn.clicked.connect(lambda _, m=medicine: self.delete_medicine(m))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(del_btn)
            actions_widget.setLayout(actions_layout)
            
            self.table.setCellWidget(row, 4, actions_widget)

    def on_search(self, text: str):
        """Handle search input."""
        if len(text) >= 2:
            medicines = Medicine.search(text)
        else:
            medicines = Medicine.get_all()
        self.load_medicines(medicines)

    def show_add_dialog(self):
        """Show add medicine dialog."""
        dialog = MedicineDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def show_edit_dialog(self, medicine: Medicine):
        """Show edit medicine dialog."""
        dialog = MedicineDialog(self, medicine)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def delete_medicine(self, medicine: Medicine):
        """Delete a medicine."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete medicine '{medicine.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            medicine.delete()
            self.refresh()


class MedicineDialog(QDialog):
    """Dialog for adding/editing medicines."""

    def __init__(self, parent, medicine: Medicine = None):
        super().__init__(parent)
        self.medicine = medicine
        self.setWindowTitle("Add Medicine" if medicine is None else "Edit Medicine")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        if self.medicine:
            self.name_input.setText(self.medicine.name)
        
        # Category with predefined options
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
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #8e44ad; }
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
        """Save medicine."""
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


def get_all_medicines_for_selection() -> List[Medicine]:
    """Helper function to get all medicines for prescription selection."""
    return Medicine.get_all()


def search_medicines_for_selection(query: str) -> List[Medicine]:
    """Helper function to search medicines for prescription selection."""
    return Medicine.search(query) if len(query) >= 2 else Medicine.get_all()