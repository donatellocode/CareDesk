from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError


class PatientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=150)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    gender = SelectField('Gender', choices=[('', 'Select...'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    notes = TextAreaField('Notes', validators=[Optional()])


class AppointmentForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    status = SelectField('Status', choices=[('waiting', 'Waiting'), ('completed', 'Completed'), ('cancelled', 'Cancelled')])
    notes = TextAreaField('Notes', validators=[Optional()])


class VisitForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    appointment_id = SelectField('Related Appointment', coerce=int, validators=[Optional()])
    diagnosis = TextAreaField('Diagnosis', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])


class MedicineForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    category = StringField('Category', validators=[Optional(), Length(max=50)])
    default_dose = StringField('Default Dose', validators=[Optional(), Length(max=100)])
    instructions = TextAreaField('Instructions', validators=[Optional()])


class PrescriptionForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    visit_id = SelectField('Related Visit', coerce=int, validators=[Optional()])
    date = DateField('Date', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])


class PrescriptionItemForm(FlaskForm):
    medicine_id = SelectField('Medicine', coerce=int, validators=[DataRequired()])
    dose = StringField('Dose', validators=[DataRequired(), Length(max=100)])
    instructions = TextAreaField('Instructions', validators=[Optional()])


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[Optional()])
