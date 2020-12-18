from flask_wtf import FlaskForm
from wtforms.widgets.core import TextArea
from wtforms.fields.core import IntegerField, SelectField, StringField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length, NumberRange

from app import db
from geo import countries


class RegisterForm(FlaskForm):
    email = EmailField(
        validators=[InputRequired(),
            Email("Email is not valid.")],
        render_kw={"placeholder": "Email"}
        )
    password = PasswordField(
        validators=[InputRequired(),
            Length(min=4, message="This password is too short. Must have at least 4 characters.")],
        render_kw={"placeholder": "Password"}
        )
    confirm_pass = PasswordField(
        validators=[InputRequired(),
            EqualTo("password", "Password does not match."),
            Length(4)],
        render_kw={"placeholder": "Confirm Password"}
        )


class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(),
            Length(4, 15)],
        render_kw={"placeholder": "Username"}
        )
    password = PasswordField(
        validators=[InputRequired(),
            Length(4, message="This password is too short. Must have at least 4 characters.")],
        render_kw={"placeholder": "Password"}
        )


class AfterLoginForm(FlaskForm):
    submit = SubmitField("Submit")


class BusinessForm(AfterLoginForm):
    name = StringField("Name",
        validators=[InputRequired(),
            Length(2, 15, "Name does not respect our rules.")]
        )
    description = StringField("Description",
        widget=TextArea()
        )
    fiscal_number = StringField("Fiscal number",
        validators=[InputRequired(),
            Length(8, 15, "Tax number isn't valid.")]
        )
    phone = StringField("Phone",
        validators=[InputRequired(),
            Length(6, 20, "Phone number isn't valid.")]
        )
    mobile = StringField("Mobile",
        validators=[InputRequired(),
            Length(6, 20, "Mobile number isn't valid.")]
        )
        
    def get_areas():
        query = db.execute("SELECT id, designation FROM businessAreas")
        sectors = list()

        for value in query:
            sectors.append((value["id"], value["designation"]))
        return sectors

    activity_sector = SelectField("Sector",
        choices=get_areas()
        )


class CustomerForm(AfterLoginForm):
    first_name = StringField("First name",
        validators=[InputRequired(),
            Length(2, 15)]
        )
    last_name = StringField("Last name",
        validators=[InputRequired(),
            Length(2, 30)]
        )
    age = IntegerField("Age",
        validators=[InputRequired(),
            NumberRange(16, 100, "It's not a valid age.")]
        )


class AccountForm(FlaskForm):
    update = SubmitField("Update")

   
class CustomerAccountForm(LoginForm, AccountForm):
    email = EmailField("Email",
        validators=[InputRequired(),
            Email("Email is not valid.")]
        )


class BusinessAccountForm(CustomerAccountForm, AccountForm):
    name = StringField("Name",
        validators=[InputRequired(),
            Length(2, 15, "Name does not respect our rules.")]
        )
    description = StringField("Description",
        widget=TextArea()
        )
    phone = StringField("Phone",
        validators=[InputRequired(),
            Length(6, 20, "Phone number isn't valid.")]
        )
    mobile = StringField("Mobile",
        validators=[InputRequired(),
            Length(6, 20, "Mobile number isn't valid.")]
        )


class AddressAccountForm(AccountForm):
    street = StringField("Address",
        validators=[InputRequired(),
            Length(5, 50)]
        )
    number = IntegerField("Number",
        validators=[InputRequired(),
            NumberRange(min=1, max=9999)]
        )
    city = StringField("City",
        validators=[InputRequired(),
            Length(2, 30, "City not valid")]
        )
    region = StringField("Region",
        validators=[InputRequired(),
            Length(2, 30, "Region not valid.")]
        )

    def country_list():
        countries_name = list()
        for country in countries:
            countries_name.append(country["name"])
        return countries_name

    country = SelectField("Country",
        choices=country_list()
        )
    zip_code = StringField("Zipcode",
        validators=[InputRequired(),
            Length(4, 10, "Zipcode is not valid.")]
        )


class StoreForm(AddressAccountForm):
    name = StringField("Name",
        validators=[InputRequired(),
            Length(2, 25, "Name does not respect our rules.")]
        )
    edit_button = SubmitField("Edit")
    add_button = SubmitField("Add")