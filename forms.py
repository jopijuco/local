from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields.core import DateField, IntegerField, SelectField, StringField
from wtforms.fields.simple import PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired


class RegisterForm(FlaskForm):
    email = EmailField([Email(), validators.input_required()], render_kw={"placeholder": "Email"})
    password = PasswordField([validators.input_required(), validators.length(min=4)], render_kw={"placeholder": "Password"})
    confirm_pass = PasswordField([validators.input_required(), validators.length(min=4)], render_kw={"placeholder": "Confirm Password"})

    def validate_email(form, field):
        if len(field.data) < 4:
            return False
    
    def validate_password(form, field):
        if len(field.data) < 4:
            return False
    
    def validate_confirm_pass(form, field):
        if len(field.data) < 4:
            return False


class LoginForm(FlaskForm):
    username = StringField([validators.input_required(), validators.length(min=4, max=15)], render_kw={"placeholder": "Username"})
    password = PasswordField([validators.input_required(), validators.length(min=4)], render_kw={"placeholder": "Password"})

    def validate_username(form, field):
        if len(field.data) < 4 or len(field.data) > 15:
            return False
    
    def validate_password(form, field):
        if len(field.data) < 4:
            return False


class CustomerForm(FlaskForm):
    first_name = StringField("First name")
    last_name = StringField("Last name")
    email = EmailField("Email")
    password = PasswordField("Password")
    confirm_password = PasswordField("Confirm Password")
    fiscal_number = StringField([InputRequired("Fiscal number"), validators.length(min=9, max=15)])
    birthday = DateField("Birth date")
    address = StringField("Address")
    street_number = IntegerField("Street number", [InputRequired(), validators.length(min=1, max=4)])
    floor = StringField("Floor", [validators.length(min=1, max=10)])
    city = StringField("City", [InputRequired(), validators.length(min=4, max=4)])
    region = StringField("Region", [InputRequired(), validators.length(min=4, max=4)])
    country = SelectField("Country")
    zipcode = IntegerField("Zipcode", [InputRequired(), validators.length(min=4, max=9)])


class BusinessForm(FlaskForm):
    pass