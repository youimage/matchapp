"""
WTForms definitions for the generic matching app.
Includes forms for registration, login, and profile management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


class RegistrationForm(FlaskForm):
    """User registration form."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    """Profile editing form."""
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    age = IntegerField('Age', validators=[
        Optional(),
        NumberRange(min=18, max=120, message='Age must be between 18 and 120')
    ])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-binary'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[Optional()])
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio must be less than 500 characters')
    ])
    tags = StringField('Interests/Tags', validators=[
        Optional(),
        Length(max=500, message='Tags must be less than 500 characters')
    ], description='Separate multiple interests with commas (e.g., hiking, reading, music)')
    location = StringField('Location', validators=[
        Optional(),
        Length(max=100, message='Location must be less than 100 characters')
    ])
    submit = SubmitField('Update Profile')


class MessageForm(FlaskForm):
    """Message form for chat functionality."""
    content = TextAreaField('Message', validators=[
        DataRequired(message='Message cannot be empty'),
        Length(min=1, max=1000, message='Message must be between 1 and 1000 characters')
    ])
    submit = SubmitField('Send Message')