from model.store import Store
from constants import CUSTOMER, LOGIN
from functools import wraps
from flask import session, request, redirect, url_for
from geo import countries

from app import db
from controller import session
from constants import IMG_DEFAULT
from model.picture import *


# Login Required Decorator
# https://flask.palletsprojects.com/en/1.0.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for(LOGIN, next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# trying to create a decorator to validate user access to certain routes
#def user_access(f):
#    @wraps(f)
#    def decorated_function(*args, **kwargs):
#        if session["user_type"] == CUSTOMER:
#
#        return f(*args, **kwargs)
#    return decorated_functions


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


def get_status():
    status_list = list()
    status = db.execute("SELECT id, name FROM status")
    for row in status:
        status_list.append(tuple((row["id"], row["name"])))
    return status_list


def get_product_image(id):
    imgs = db.execute("SELECT file FROM imgs AS i INNER JOIN product_img AS pi ON i.id = pi.img_id AND pi.product_id = :id",
        id=id)
    
    if len(imgs) >= 1:
        pic = Picture("", imgs[0]["file"], "")
        pic.name_thumbnail()
    else:
        pic = Picture("", IMG_DEFAULT, IMG_DEFAULT)
    main_img = pic.thumbnail
    return main_img


def is_owner(id):
    business = db.execute(f"SELECT id FROM business WHERE user_id = :user", user=session["user_id"])
    return business[0]["id"] == id


def display_stores(business_stores):
    stores = list()
    for row in business_stores:
        if not row["front_pic"]:
            pic = Picture("", IMG_DEFAULT, IMG_DEFAULT)
            picture = pic.thumbnail
        else:
            front_pic = row["front_pic"]
            pic = Picture("", front_pic, "")
            pic.name_thumbnail() 
            picture = pic.thumbnail
        
        store = Store(row["id"], row["name"], picture, row["number"], row["street"], row["zip_code"], row["city"],
            row["region"], row["country"])
        stores.append(store)
    
    return stores