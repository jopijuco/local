from datetime import datetime
from logging import exception
from os import remove
from basket_manager import Basket_Manager
import re
from sqlite3.dbapi2 import Error

from flask.helpers import make_response, url_for
from application import app, db
from constants import *
from flask import render_template, request, session
from utils import login_required
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image, ImageOps
from model.business import *
from model.store import *
from model.product import *
from model.picture import *
from model.order import *

import ast
import os

bm = Basket_Manager()

@app.route("/")
def index():
    stores = db.execute("SELECT id, name FROM stores")
    return render_template(INDEX_PAGE, stores=stores)


@app.route("/register", methods=[GET, POST])
def register():
    if request.method == POST:
        email = request.form.get("email")
        username = email[:email.find("@")]

        if request.form.get("type_options") == BUSINESS:
            check_user = db.execute("SELECT * FROM user_businesses WHERE username = :username OR email = :email",
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
            check_user = db.execute("SELECT * FROM user_customers WHERE username = :username OR email = :email",
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


@app.route("/login", methods=[GET, POST])
def login():
    if request.method == POST:
        session.clear()

        if request.form.get("type_options") == BUSINESS:
            table = BUSINESS_TABLE
            user_type = BUSINESS
        else:
            table = CUSTOMER_TABLE
            user_type = CUSTOMER
        
        user = db.execute(f"SELECT * FROM {table} WHERE username = :username", username=request.form.get("username"))
        # password validation commented to allow to debug with "test users"
        # or not check_password_hash(user[0]["hash_pass"], request.form.get("password"))
        if len(user) != 1:
            return "FAILED LOGIN"
        
        session["user_id"] = user[0]["id"]
        session["type"] = user_type
        return redirect(url_for(INDEX))

    return render_template(LOGIN_PAGE)


@app.route("/shop/<id>")
def shop(id):
    products = db.execute(f"SELECT p.id AS prd_id, p.name AS name, p.description AS description, ps.price AS price, s.id AS shop_id, s.name AS shop FROM stores AS s INNER JOIN product_store AS ps ON s.id = ps.store_id AND s.id = {id} INNER JOIN products AS p ON ps.product_id = p.id")
    return render_template("shop_products.html", products=products, name=products[0]["shop"])


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
            db.execute("INSERT INTO stores (business_id, address_id)  VALUES (:id, :address_id)", id = session["business_id"], address_id = new_address_id)
        else:
            store_id = request.form['submit_button']
            #store's image update
            if request.files["image_"+store_id]:
                file = request.files["image_"+store_id]
                extension = file.filename.split('.')[1]
                image_name="store_front_pic_"+store_id+"."+extension
                file.save(os.path.join(app.config["IMAGE_UPLOADS"], image_name))
                db.execute("UPDATE stores SET front_pic=:front_pic WHERE id= :id", front_pic = image_name, id=store_id)
                Picture('',image_name,'').create_thumbnail()
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
    hasproduct = False
    for row in db.execute("SELECT * FROM products WHERE business_id = :id", id=session["business_id"]):
        hasproduct = True
        id = row["id"]
        name = row["name"]
        description = row["description"]
        price = row["price"]
        imgs = db.execute("SELECT file FROM imgs i INNER JOIN  product_img pi ON (i.id = pi.img_id AND pi.product_id = :id)", id = id)
        if len(imgs) >= 1:
            main_img = Picture('', imgs[0]["file"],'')
            main_img.name_thumbnail() 
        else:
            main_img = Picture('', IMG_DEFAULT,IMG_DEFAULT)
        product = Product(id, name, description, price, '', '', main_img.thumbnail)
        products.append(product)
    return render_template(PRODUCT_PAGE, products=products, hasproduct = hasproduct)


@app.route("/single_product/<product_id>", methods=[GET, POST])
@login_required
def single_product(product_id):
    if request.method == POST:
        id = request.form.get("product_id")
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        #to do : discount, tag 
        discount = ""
        total = ""
        tag_id = ""
        img_id = ""
        if request.form['submit'] == 'add_product':
            product_id = db.execute("INSERT INTO products(name, description,price,discount,total,tag_id,img_id,business_id) VALUES (:name, :description, :price, :discount, :total, :tag_id, :img_id, :business_id)", name=name, description=description, price=price, discount=discount, total=total, tag_id=tag_id, img_id=img_id, business_id=session["business_id"])
        elif request.form['submit'] == 'add_product':
            db.execute("UPDATE products SET name=:name, description=:description,price=:price WHERE id=:id", name=name, description=description, price=price, id=product_id)
        elif request.form['submit'] == 'add_img':
            #product images
            if request.files["new_image"]:
                image = request.files["new_image"]
                #create the new image name
                extension = image.filename.split('.')[1]
                nb_picture = db.execute("SELECT COUNT(DISTINCT img_id) as nb FROM product_img WHERE product_id = :product_id", product_id=product_id)
                pic_number = nb_picture[0]["nb"]+1
                image_name="product_"+product_id+"_pic_"+str(pic_number)+"."+extension
                #save the new image and insert it in the DB
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image_name))
                new_img_id = db.execute("INSERT INTO imgs(file) VALUES (:image_name)", image_name=image_name)
                db.execute("INSERT INTO product_img(product_id, img_id) VALUES (:product_id, :new_img_id)", product_id=product_id, new_img_id=new_img_id)
                #create the square thumbnail
                Picture('',image_name,'').create_thumbnail()
        else:
            img_id = request.form['submit']
            image = request.files["image_"+img_id]
            new_extension = image.filename.split('.')[1]
            old_img = db.execute("SELECT file FROM imgs i WHERE id = :img_id", img_id=img_id)
            #replace old by new img (keep the same name but extension could be different)
            image_name=old_img[0]["file"].split('.')[0]+"."+new_extension       
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image_name))
            old_extension = old_img[0]["file"].split('.')[1]
            if old_extension != new_extension:
                db.execute("UPDATE imgs SET file=:file WHERE id= :id", file = image_name, id=img_id)
            #create the square thumbnail
            Picture('',image_name,'').create_thumbnail()
    product = Product(product_id, '', '', '', '', '', '')
    hasimg = False
    maximg = False
    if product_id != 'new':
        for row in db.execute("SELECT * FROM products WHERE id = :id", id=product_id):
            product.name = row["name"]
            product.description = row["description"]
            product.price = row["price"]
        #retrieve all product's images
        for row in db.execute("SELECT id, file FROM imgs i INNER JOIN  product_img pi ON (i.id = pi.img_id AND pi.product_id = :id)", id=product_id):
            pic = Picture(row["id"],row["file"],'')
            pic.name_thumbnail() 
            product.add_image(pic)
            hasimg = True
        if len(product.images) == MAX_IMG_PRODUCT:
            maximg = True
    return render_template(SINGLE_PRODUCT_PAGE, product=product, hasimg = hasimg, maximg = maximg)


@app.route("/add_basket/<product>")
def add_basket(product):
    dict_product = ast.literal_eval(product)
    
    for key in dict_product.keys():
        if key == "prd_id":
            bm.add(dict_product[key])
        elif key == "shop_id":
            bm.add(dict_product[key])

    resp = redirect(url_for(INDEX))
    resp.set_cookie("basket", str(bm.get_list()))
    return resp


@app.route("/remove_basket/<product>")
def remove_basket(product):
    dict_product = ast.literal_eval(product)

    for key in dict_product.keys():
        if key == "id":
            bm.remove(dict_product[key])
        elif key == "shop_id":
            bm.remove(dict_product[key])

    resp = redirect(url_for(BASKET))
    resp.set_cookie("basket", str(bm.get_list()))
    return resp


@app.route("/basket")
def basket():
    basket = list()
    id_p = list()
    id_s = list()

    for index, id in enumerate(bm.get_list()):
        if index % 2 == 0:
            id_p.append(id)
        else:
            id_s.append(id)
    
    for i in range(len(id_p)):
        products = db.execute(f"SELECT p.*, ps.*, s.id AS shop_id, s.name AS shop_name FROM product_store AS ps INNER JOIN products AS p ON ps.product_id = p.id AND p.id = {id_p[i]} AND ps.store_id = {id_s[i]} INNER JOIN stores AS s ON ps.store_id = s.id")
        basket.append(products)

    return render_template("basket.html", products=basket, amount=bm.total("price", basket))


@app.route("/orders/", methods=[GET, POST])
@login_required
def order():
    if session["type"] == CUSTOMER:
        if request.method == POST:
            now = datetime.now().strftime("%Y-%m-%d %H:%m:%s")
            amount = float(request.form.get("amount"))
        
            # status order and store are hardcoded bcs are not yet defined: discuss
            db.execute(f"INSERT INTO orders (date, amount, status_id, store_id, customer_id) VALUES ('{now}', {amount}, 1, 1, {session['user_id']})")
            bm.empty_basket()
            return redirect(url_for(ORDER))

        orders = db.execute(f"SELECT date, amount FROM orders WHERE customer_id = {session['user_id']}")
        return render_template(ORDER_PAGE, orders=orders)
    else:
        orders = []
        for row in db.execute(f"SELECT * FROM orders WHERE store_id IN (select id FROM stores WHERE business_id = {session['user_id']})"):
            order = Order(row["id"], row["date"], row["amount"], row["status"], row["store_id"], row["customer_id"])
            orders.append(order)
        return render_template(ORDER_PAGE, orders=orders)


@app.route("/order_details/<order_id>", methods=[GET, POST])
@login_required
def order_details(order_id):
    if request.method == POST:
        return "TODO"
    for row in db.execute("SELECT * FROM orders WHERE id = :id", id = order_id):
        order = Order(row["id"], row["date"], row["amount"], row["status"], row["store_id"], row["customer_id"])
    return render_template(ORDER_DETAILS_PAGE, order = order)


@app.route("/history", methods=[GET, POST])
@login_required
def history():
    if request.method == POST:
        return "TODO"
    return render_template(HISTORY_PAGE)


@app.route("/account", methods=[GET, POST])
@login_required
def account():  
    return render_template("account.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    bm.empty_basket()
    resp = redirect(url_for(INDEX))
    resp.set_cookie("basket", "", expires=0)
    return resp