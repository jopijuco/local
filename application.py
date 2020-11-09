from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/register")
def register():
    return "TODO"

@app.route("/login")
def login():
    return render_template("login.html")