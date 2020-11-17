from application import app
from constants import *
from flask import render_template, request, session
from sqlite3 import connect
from sqlite3.dbapi2 import Error
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
@login_required
def user():

    if request.method == POST:
        return "TODO"
    return render_template(USER_PAGE, user="LOOOL")


@app.route("/logut")
@login_required
def logout():

    session.clear()
    return redirect()