from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=6, max=120)])
    
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=120)])
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=13, max=21)])
    
    submit = SubmitField('Register')