from constants import *
from cs50 import SQL
from flask import Flask
from flask_session import Session
from tempfile import mkdtemp

import os

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOADED"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["IMAGE_UPLOADS"] = "static"
Session(app)

# Define a secret key to use CSRF
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY

# Connect to database
db = SQL(f"sqlite:///database/{DEMO_DB}")

# Start App
import controller