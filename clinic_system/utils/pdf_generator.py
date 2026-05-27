"""PDF Generator for prescriptions."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import Optional, List
from datetime import datetime


class PDFGenerator:
    """Generate professional prescription PDFs."""

    def __init__(self, clinic_name: str = "Clinic Name", 
                 doctor_name: str = "Dr. Doctor Name"):
        self.clinic_name = clinic_name
        self.doctor_name = doctor_name
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='Title_Center',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12,
            spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='PatientInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='MedicineHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12
        ))
        self.styles.add(ParagraphStyle(
            name='MedicineItem',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4
        ))
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))

    def generate_prescription(self, patient_name: str, patient_age: Optional[int],
                            patient_gender: str, date: str,
                            items: List[dict], 
                            output_path: str = "prescription.pdf") -> bool:
        """Generate a prescription PDF.
        
        Args:
            patient_name: Patient's name
            patient_age: Patient's age
            patient_gender: Patient's gender
            date: Prescription date
            items: List of dicts with keys: medicine_name, dose, instructions
            output_path: Output file path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            story = []
            
            # Header
            story.append(Paragraph(self.clinic_name, self.styles['Title_Center']))
            story.append(Paragraph(f"Dr. {self.doctor_name}", self.styles['SubTitle']))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))
            
            # Prescription info
            story.append(Paragraph(f"<b>Prescription</b>", 
                                   self.styles['Title_Center']))
            story.append(Spacer(1, 5*mm))
            
            # Patient details table
            patient_data = [
                ["Patient:", patient_name, "Date:", date],
                ["Age:", str(patient_age or "N/A"), "Gender:", patient_gender or "N/A"]
            ]
            
            patient_table = Table(patient_data, colWidths=[50, 150, 50, 100])
            patient_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 10*mm))
            
            # Medicines section
            story.append(Paragraph("<b>Medicines:</b>", self.styles['MedicineHeader']))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=6))
            
            if items:
                # Medicine table
                med_data = [["#", "Medicine", "Dose", "Instructions"]]
                for i, item in enumerate(items, 1):
                    med_data.append([
                        str(i),
                        item.get('medicine_name', ''),
                        item.get('dose', ''),
                        item.get('instructions', '')
                    ])
                
                med_table = Table(med_data, colWidths=[25, 80, 80, 130])
                med_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ]))
                story.append(med_table)
            else:
                story.append(Paragraph("No medicines prescribed.", 
                                      self.styles['MedicineItem']))
            
            story.append(Spacer(1, 15*mm))
            
            # Signature
            story.append(Paragraph(f"<b>Dr. {self.doctor_name}</b>", 
                                   ParagraphStyle(name='Sig', alignment=TA_RIGHT, fontSize=12)))
            story.append(Spacer(1, 5*mm))
            
            # Footer
            footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            story.append(Paragraph(footer_text, self.styles['Footer']))
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

    def generate_patient_report(self, patient: dict, visits: List[dict],
                              output_path: str = "patient_report.pdf") -> bool:
        """Generate a patient history report PDF."""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            story = []
            
            # Header
            story.append(Paragraph("Patient History Report", 
                                   self.styles['Title_Center']))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))
            
            # Patient info
            story.append(Paragraph(f"<b>Patient:</b> {patient.get('name', 'N/A')}", 
                                   self.styles['PatientInfo']))
            story.append(Paragraph(f"<b>Age:</b> {patient.get('age', 'N/A')}  "
                                   f"<b>Gender:</b> {patient.get('gender', 'N/A')}  "
                                   f"<b>Phone:</b> {patient.get('phone', 'N/A')}", 
                                   self.styles['PatientInfo']))
            story.append(Spacer(1, 10*mm))
            
            # Visits history
            story.append(Paragraph("<b>Visit History:</b>", 
                                   self.styles['MedicineHeader']))
            
            for i, visit in enumerate(visits, 1):
                story.append(Paragraph(f"<b>Visit {i} - {visit.get('date', '')}</b>", 
                                      self.styles['MedicineItem']))
                story.append(Paragraph(f"Diagnosis: {visit.get('diagnosis', 'N/A')}", 
                                      self.styles['MedicineItem']))
                story.append(Paragraph(f"Notes: {visit.get('notes', 'N/A')}", 
                                      self.styles['MedicineItem']))
                story.append(Spacer(1, 5*mm))
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return False