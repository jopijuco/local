from flask_wtf import FlaskForm
from geo import countries
from wtforms.fields.core import DateField, IntegerField, SelectField, StringField
from wtforms.fields.simple import PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length


class RegisterForm(FlaskForm):
    email = EmailField(
        validators=[
            Email("Not a valid email address"),
            DataRequired("Must submit an email."),
            Length(min=8, message="Not a valid email address")],
        render_kw={"placeholder": "Email"}
        )
    password = PasswordField(
        validators=[
            DataRequired("Must submit a password"),
            Length(min=4, message="This password is too short. Must have at least 4 characters.")],
        render_kw={"placeholder": "Password"}
        )
    confirm_pass = PasswordField(
        validators=[
            EqualTo("password", "Passwords must match."),
            Length(4)],
        render_kw={"placeholder": "Confirm Password"}
        )


class LoginForm(FlaskForm):
    username = StringField(
        validators=[
            DataRequired("Must provide your username"),
            Length(4, 15, "Username is not valid. Try again.")],
        render_kw={"placeholder": "Username"}
        )
    password = PasswordField(
        validators=[
            DataRequired("Must provide your password."),
            Length(4, message="Password is incorrect. Try again.")],
        render_kw={"placeholder": "Password"}
        )


class CustomerAccountForm(FlaskForm):
    first_name = StringField("First name",
        validators=[Length(15)]
        )
    last_name = StringField("Last name",
        validators=[Length(20)]
        )
    age = IntegerField("Age",
        validators=[Length(16, 100, "This number is not valid")]
        )


class UserAccountForm(FlaskForm):
    email = EmailField("Email")
    password = PasswordField("Password",
        validators=[Length(4, message="")]
        )


class AddressAccountForm(FlaskForm):
    street = StringField("Address")
    number = IntegerField("Street number",
        validators=[Length(min=1, max=9999)]
        )
    floor = StringField("Floor",
        validators=[Length(1, 8, "Floor is not valid.")]
        )
    city = StringField("City",
        validators=[Length(2, 30, "City not valid")]
        )
    region = StringField("Region",
        validators=[Length(2, 30, "Region not valid.")]
        )

    def country_list():
        countries_name = list()
        for country in countries:
            countries_name.append(country["name"])
        return countries_name

    country = SelectField("Country",
        choices=country_list()
        )
    zip_code = IntegerField("Zipcode",
        validators=[Length(4, 10, "Zipcode is not valid.")]
        )


class BusinessForm(FlaskForm):
    #name
    #description
    #fiscal_number
    #phone
    #mobile
    pass