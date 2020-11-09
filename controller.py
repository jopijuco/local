from application import app, conn
from flask import render_template

@app.route("/")
def index():
    return render_template("index.html", conn=conn)

@app.route("/register")
def register():
    return "TODO"

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/user")
def user():
    return "TODO"