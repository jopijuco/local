from sqlite3.dbapi2 import Error

from flask.helpers import url_for
from application import app, db
from constants import *
from flask import render_template, request, session
from utils import login_required
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash, generate_password_hash
from model.business import *
from model.store import *
import os


@app.route("/")
def index():
    return render_template(INDEX_PAGE)


@app.route("/register", methods=[GET, POST])
def register():

    if request.method == POST:
        email = request.form.get("email")
        username = email[:email.find("@")]

        check_user = db.executef("SELECT * FROM user_businesses WHERE username = :username OR email = :email",
                                    username=username,
                                    email=email)

        if len(check_user) >= 1:
            return "USER ALREADY EXISTS"
        
        password = request.form.get("password")
        db.execute("INSERT INTO user_businesses (username, email, hash_pass) VALUES (:username, :email, :hash_pass)",
                    username=username,
                    email=email,
                    hash_pass=generate_password_hash(password, "sha256"))
        
        return redirect(url_for(LOGIN))

    return render_template(REGISTER_PAGE)


@app.route("/login", methods=[GET, POST])
def login():

    if request.method == POST:
        session.clear()
        try:    
            user = db.execute("SELECT * FROM user_businesses WHERE username = :username",
                                username=request.form.get("username"))
        except Error as e:
            return e.args

        # password validation commented to allow to debug with "test users"
        # or not check_password_hash(user[0]["hash_pass"], request.form.get("password"))
        if len(user) != 1:
            return "FAILED LOGIN"

        session["user_id"] = user[0]["id"]      
        return redirect(url_for("area", username=user[0]["username"]))

    return render_template(LOGIN_PAGE)


@app.route("/area/<username>")
@login_required
def area(username):
    return render_template("area.html", username=username)


@app.route("/store", methods=[GET, POST])
@login_required
def store():
    if request.method == POST:
        if request.form['submit_button'] == 'submit business':
            name = request.form.get("name")
            description = request.form.get("description")
            mobile = request.form.get("mobile")
            phone = request.form.get("phone")
            fiscal_number = request.form.get("fiscal_number")
            
            db.execute("UPDATE business SET name = :name, fiscal_number = :fiscal_number, description = :description, mobile = :mobile, phone = :phone WHERE id = :id",
                        name=name, description=description, fiscal_number=fiscal_number, mobile=mobile, phone=phone,
                        id=session["user_id"])
        
        elif request.form['submit_button'] == 'submit store':
            if request.files:
                image = request.files["image"]
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
                print("image saved")
                front_pic=image.filename
                
                db.execute("UPDATE stores SET front_pic = :front_pic WHERE business_id = :id",
                            front_pic=front_pic, id=session["user_id"])
                
                #return redirect(request.url)


    business = Business(session["user_id"], '', '', '', '', '')
    for row in db.execute("SELECT * FROM business WHERE id = :id", id=session["user_id"]):
        business.name = row["name"]
        business.description = row["description"]
        business.fiscal_number = row["fiscal_number"]
        business.phone = row["phone"]
        business.mobile = row["mobile"]
    #only one store is retrieve for the moment
    store = Store('','')
    for row in db.execute("SELECT * FROM stores WHERE business_id = :id", id=session["user_id"]):
        store.id = row["id"]
        if (row["front_pic"] != ""):
            store.front_pic = row["front_pic"]
        else:
            store.front_pic = "noimgavailable.jpg"

    return render_template(STORE_PAGE, business=business, store=store)


@app.route("/product", methods=[GET, POST])
@login_required
def product():
    if request.method == POST:
        return "TODO"
    return render_template(PRODUCT_PAGE, product="product name")


@app.route("/order", methods=[GET, POST])
@login_required
def order():
    if request.method == POST:
        return "TODO"
    return render_template(ORDER_PAGE)


@app.route("/history", methods=[GET, POST])
@login_required
def history():
    if request.method == POST:
        return "TODO"
    return render_template(HISTORY_PAGE)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for(INDEX))