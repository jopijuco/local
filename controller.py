from sqlite3.dbapi2 import Error
from application import app, db
from constants import *
from flask import render_template, request, session
from utils import login_required
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash, generate_password_hash


@app.route("/")
def index():
    return render_template(INDEX_PAGE)


@app.route("/register", methods=[GET, POST])
def register():

    if request.method == POST:
        email = request.form.get("email")
        username = email[:email.find("@")]

        check_user = db.execute("SELECT * FROM user_customers WHERE username = :username OR email = :email",
                                    username=username,
                                    email=email)

        if len(check_user) >= 1:
            return "USER ALREADY EXISTS"
        
        password = request.form.get("password")
        user = db.execute("INSERT INTO user_customers (username, email, hash_pass) VALUES (:username, :email, :hash_pass)",
                            username=username,
                            email=email,
                            hash_pass=generate_password_hash(password, "sha256"))
        
        return redirect(LOGIN)

    return render_template(REGISTER_PAGE)


@app.route("/login", methods=[GET, POST])
def login():

    #session.clear()

    if request.method == POST:
        try:    
            user = db.execute("SELECT * FROM user_customers WHERE username = :username",
                                username=request.form.get("username"))
        except Error as e:
            return e.args

        if len(user) != 1 or not check_password_hash(user[0]["hash_pass"], request.form.get("password")):
            return "FAILED LOGIN"

        session["user_id"] = user[0]["id"]
        return redirect(USER)

    return render_template(LOGIN_PAGE)


@app.route("/user", methods=[GET, POST])
@login_required
def user():

    if request.method == POST:
        return "TODO"
    return render_template(USER_PAGE)


@app.route("/logut")
@login_required
def logout():

    session.clear()
    return redirect()