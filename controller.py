from application import app
from constants import *
from flask import render_template, request, session
from sqlite3 import connect
from sqlite3.dbapi2 import Error
from cs50 import SQL
from utils import login_required
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash, generate_password_hash
from model import *


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database/local_dev.db")

@app.route("/")
def index():
    session["user_id"] = 1
    name= ""
    for row in db.execute("SELECT * FROM business WHERE id = :id", id=session["user_id"]):
        name = row["name"]
    return render_template(INDEX_PAGE, name = name)


@app.route("/register", methods=[GET, POST])
def register():

    if request.method == POST:
        email = request.form.get("email")
        username = email[0:email.find("@")]
        hash_pass = generate_password_hash(request.form.get("password"), "sha256")

        with connect(DEV_DB) as conn:
            cur = conn.cursor()
            cur.execute("INSERT TABLE user_customers (username, email, hash_pass) VALUES (?, ?, ?)",
                        username, email, hash_pass)
        
        return redirect(LOGIN)

    return render_template(REGISTER_PAGE)


@app.route("/login", methods=[GET, POST])
def login():

    if request.method == POST:
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        with connect(DEV_DB) as conn:
            cur = conn.cursor()
            
            user = cur.execute("SELECT * FROM user_customers WHERE username = ? AND password = ?",
                            username, password)
            
            if len(user) is 1:
                return redirect(USER)
            return "INVALID CREDENTIALS"

    return render_template(LOGIN_PAGE)


@app.route("/user", methods=[GET, POST])
#@login_required
def user():
    if request.method == POST:
        return "TODO"
    return render_template(USER_PAGE, user="LOOOL")

@app.route("/store", methods=[GET, POST])
#@login_required
def store():
    if request.method == POST:
       #business data
        name = request.form.get("name")
        description = request.form.get("description")
        mobile = request.form.get("mobile")
        phone = request.form.get("phone")
        db.execute("UPDATE business SET name=:newName, description=:newDescription , mobile=:newMobile , phone=:newPhone  WHERE id= :id", newName=name, newDescription=description, newMobile=mobile, newPhone=phone, id=session["user_id"])
        #addresses  data
        #assuming that a business have an entry in address table (could be create automatically when registered)
        for row in db.execute("SELECT address_id FROM business WHERE id = :id", id=session["user_id"]):
            address_id = row["address_id"]
        number = request.form.get("number")
        street = request.form.get("street")
        zipcode = request.form.get("zipcode")
        city = request.form.get("city")
        region = request.form.get("region")
        country = request.form.get("country")
        db.execute("UPDATE addresses SET number=:number, street=:street, zip_code=:zipcode , city=:city , region=:region, country=:country  WHERE id= :address_id", number=number, street=street, zipcode=zipcode, city=city, region=region, country=country, address_id=address_id)

    store = Business(session["user_id"], '', '', '', '', '', '', '', '', '', '', '', '')
    for row in db.execute("SELECT * FROM business b LEFT JOIN addresses a ON (a.id = b.address_id) WHERE b.id = :id", id=session["user_id"]):
        store.name = row["name"]
        store.description = row["description"]
        store.address_number = row["number"]
        store.address_street = row["street"]
        store.address_zip_code = row["zip_code"]
        store.address_city = row["city"]
        store.address_region = row["region"]
        store.address_country = row["country"]
        store.phone = row["phone"]
        store.mobile = row["mobile"]
        #store.email = ""
        store.picture = ""
    return render_template(STORE_PAGE, store = store)

@app.route("/product", methods=[GET, POST])
#@login_required
def product():
    if request.method == POST:
        return "TODO"
    return render_template(PRODUCT_PAGE, product="product name")

@app.route("/order", methods=[GET, POST])
#@login_required
def order():
    if request.method == POST:
        return "TODO"
    return render_template(ORDER_PAGE)

@app.route("/history", methods=[GET, POST])
#@login_required
def history():
    if request.method == POST:
        return "TODO"
    return render_template(HISTORY_PAGE)

@app.route("/logut")
@login_required
def logout():

    session.clear()
    return redirect()