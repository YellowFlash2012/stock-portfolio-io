from xmlrpc.client import Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=6, max=120)])
    
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=120)])
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=13, max=21)])
    
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])

    password = PasswordField('Password', validators=[DataRequired()])

    remember_me = BooleanField('Remember me')

    submit = SubmitField('Login')

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    submit = SubmitField('Submit')

class PasswordForm(FlaskForm):
    password = PasswordField('New Password: ', validators=[DataRequired(), Length(min=13, max=21)])
    submit = SubmitField('Submit')