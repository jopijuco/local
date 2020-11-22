import re
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
from model.product import *
import os


@app.route("/")
def index():
    return render_template(INDEX_PAGE)

@app.route(f"/{CUSTOMER}")
@app.route(f"/{BUSINESS}")
def user_type():
    arg = request.path[request.path.find("/")+1:]
    return render_template(USERTYPE_PAGE, user=arg)


@app.route(f"/{CUSTOMER}/register", methods=[GET, POST])
@app.route(f"/{BUSINESS}/register", methods=[GET, POST])
def register():
    arg = request.path[request.path.find("/")+1:request.path.rfind("/")]

    if request.method == POST:
        email = request.form.get("email")
        username = email[:email.find("@")]

        if arg == BUSINESS:
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
        else:
            check_user = db.executef("SELECT * FROM user_customers WHERE username = :username OR email = :email",
                                        username=username,
                                        email=email)
            if len(check_user) >= 1:
                return "USER ALREADY EXISTS"
        
            password = request.form.get("password")
            db.execute("INSERT INTO user_customers (username, email, hash_pass) VALUES (:username, :email, :hash_pass)",
                        username=username,
                        email=email,
                        hash_pass=generate_password_hash(password, "sha256"))

        return redirect(url_for(LOGIN))
    return render_template(REGISTER_PAGE)


@app.route(f"/{CUSTOMER}/login", methods=[GET, POST])
@app.route(f"/{BUSINESS}/login", methods=[GET, POST])
def login():
    arg = request.path[request.path.find("/")+1:request.path.rfind("/")]
    
    if request.method == POST:
        session.clear()

        if arg == BUSINESS:
            user = db.execute("SELECT u.*, b.id as business_id FROM user_businesses u LEFT JOIN business b ON (u.id=b.user_id) WHERE username = :username",
                                username=request.form.get("username"))
        else:
            user = db.execute("SELECT * FROM user_customers WHERE username = :username",
                                username=request.form.get("username"))
        # password validation commented to allow to debug with "test users"
        # or not check_password_hash(user[0]["hash_pass"], request.form.get("password"))
        if len(user) != 1:
            return "FAILED LOGIN"

        session["user_id"] = user[0]["id"] 
        session["business_id"] = user[0]["business_id"] 

        return redirect(url_for("area", username=user[0]["username"]))

    return render_template(LOGIN_PAGE, user=arg)


@app.route("/area/<username>")
#@login_required
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
            db.execute("UPDATE business SET name=:name, fiscal_number=:fiscal_number, description=:description , mobile=:mobile , phone=:phone  WHERE id= :id", name=name, description=description, fiscal_number=fiscal_number, mobile=mobile, phone=phone, id=session["business_id"])
        elif request.form['submit_button'] == 'add_store':
            new_address_id = db.execute("INSERT INTO addresses (street, number, zip_code, city, region, country) VALUES ('', '', '', '', '', '')")
            db.execute("INSERT INTO stores (business_id, address_id)  VALUES (:id, :address_id)", id=session["business_id"], address_id=new_address_id)
        else:
            store_id = request.form['submit_button']
            #store's image update
            if request.files["image_"+store_id]:
                image = request.files["image_"+store_id]
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
                front_pic=image.filename
                db.execute("UPDATE stores SET front_pic=:front_pic WHERE id= :id", front_pic = front_pic, id=store_id)
            #store's address update
            number = request.form.get("number_"+store_id)
            street = request.form.get("street_"+store_id)
            zip_code = request.form.get("zip_code_"+store_id)
            region = request.form.get("region_"+store_id)
            city = request.form.get("city_"+store_id)
            country = request.form.get("country_"+store_id)
            db.execute("UPDATE addresses SET number=:number, street=:street, zip_code=:zip_code, city=:city, region=:region, country=:country WHERE id= (SELECT address_id FROM stores WHERE id=:id)", number = number, street = street, zip_code = zip_code, city = city, region = region, country = country, id=store_id)

    business = Business(session["business_id"], '', '', '', '', '')
    for row in db.execute("SELECT * FROM business WHERE id = :id", id=session["business_id"]):
        business.name = row["name"]
        business.description = row["description"]
        business.fiscal_number = row["fiscal_number"]
        business.phone = row["phone"]
        business.mobile = row["mobile"]
    
    for row in db.execute("SELECT s.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM stores s LEFT JOIN addresses a ON (a.id = s.address_id) WHERE business_id = :id", id=session["business_id"]):
        if (row["front_pic"] is None or row["front_pic"] == ""):
            front_pic = IMG_DEFAULT
        else:
            front_pic = row["front_pic"]
        store = Store(row["id"],front_pic,row["number"],row["street"],row["zip_code"],row["city"],row["region"],row["country"])
        business.add_store(store)
    
    return render_template(STORE_PAGE, business =  business)

@app.route("/product", methods=[GET, POST])
@login_required
def product():
    if request.method == POST:
        if request.form['submit'] == 'add':
            return redirect(url_for("single_product", product_id = 'new'))
    products = []
    for row in db.execute("SELECT * FROM products WHERE business_id = :id", id=session["business_id"]):
        id = row["id"]
        name = row["name"]
        description = row["description"]
        imgs = db.execute("SELECT file FROM imgs i INNER JOIN  product_img pi ON (i.id = pi.img_id AND pi.product_id = :id)", id=id)
        print(imgs)
        if len(imgs) >= 1:
            print("img found")
            main_img = imgs[0]["file"] 
        else:
            main_img  = IMG_DEFAULT
        product = Product(id, name, description, '', '', '', main_img)
        products.append(product)
    return render_template(PRODUCT_PAGE, products=products)


@app.route("/single_product/<product_id>", methods=[GET, POST])
@login_required
def single_product(product_id):
    if request.method == POST:
        print("post")
        id = request.form.get("product_id")
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        #to do : discount, tag and img
        discount = ""
        total = ""
        tag_id = ""
        img_id = ""
        if request.form['submit'] == 'add':
            print("add a product")
            product_id = db.execute("INSERT INTO products(name, description,price,discount,total,tag_id,img_id,business_id) VALUES (:name, :description, :price, :discount, :total, :tag_id, :img_id, :business_id)", name=name, description=description, price=price, discount=discount, total=total, tag_id=tag_id, img_id=img_id, business_id=session["business_id"])
        else:
            db.execute("UPDATE products SET name=:name, description=:description,price=:price WHERE id=:id", name=name, description=description, price=price, id=product_id)
    
    product = Product(product_id, '', '', '', '', '', '')
    if product_id != 'new':
        for row in db.execute("SELECT * FROM products WHERE id = :id", id=product_id):
            product.name = row["name"]
            product.description = row["description"]
            product.price = row["price"]
            product.main_img  = IMG_DEFAULT
    return render_template(SINGLE_PRODUCT_PAGE, product=product)

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