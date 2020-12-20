from constants import LOGIN
from functools import wraps
from flask import session, request, redirect, url_for
from geo import countries

from app import db
from controller import session


# Login Required Decorator
# https://flask.palletsprojects.com/en/1.0.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for(LOGIN, next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_countries():
    countries_name = list()
    for country in countries:
        countries_name.append(country["name"])
    return countries_name


def validate_user(id):
    validate_user = db.execute(f"SELECT s.id FROM stores AS s INNER JOIN business AS b ON s.business_id = b.id WHERE s.id = :store AND b.user_id = :user",
        store=id, user=session['user_id'])
    
    if int(id) is not validate_user[0]["id"]:
        return "You have no permission to access this page"