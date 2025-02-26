from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email, Length, ValidationError

class ConfigAccountForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    direccion = StringField('Dirección', validators=[Length(max=200)])
    doc_identidad = StringField('Documento de Identidad', validators=[Length(max=20)])
    submit = SubmitField('Guardar Cambios')

class PublicacionForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(min=5, max=100)])
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(min=10, max=500)])
    precio = DecimalField('Precio', validators=[DataRequired()])
    distrito = StringField('Distrito', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('Vivienda', 'Vivienda'), ('Vehículo', 'Vehículo')]) 