from flask import render_template, request, session
from flask.helpers import url_for
from werkzeug.datastructures import MultiDict
from forms import *
from basket_manager import *
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect

from app import app, db
from basket_manager import Basket_Manager
from constants import *
from forms import *
from model.business import *
from model.store import *
from model.product_management import *
from model.picture import *
from model.order import *
from model.status import *
from model.customer import *
from utils import login_required


import ast
import os

bm = Basket_Manager()

@app.route("/")
def index():
    stores = []
    #store without products (or with product with stock<1) are not display for user/customer
    all_stores_query = db.execute("SELECT s.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM stores s LEFT JOIN addresses a ON (a.id = s.address_id) WHERE s.id IN (SELECT store_id FROM product_store WHERE stock>0)")
    message = None
    isShopping = True
    try:
        if session['type'] == BUSINESS:
            isShopping = False
            stores_query = db.execute("SELECT s.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM stores s LEFT JOIN addresses a ON (a.id = s.address_id) WHERE business_id=:id", id=session["business_id"])
            if not stores_query:
                message = "You don't have any registered stores."
        if session['type'] == CUSTOMER:    
            stores_query = all_stores_query
    except KeyError:
        stores_query = all_stores_query

    for row in stores_query:
        if (row["front_pic"] is None or row["front_pic"] == ""):
            picture = IMG_DEFAULT
        else:
            front_pic = row["front_pic"]
            pic = Picture('', front_pic,'')
            pic.name_thumbnail() 
            picture = pic.thumbnail
        store = Store(row["id"],row["name"],picture,row["number"],row["street"],row["zip_code"],row["city"],row["region"],row["country"])
        stores.append(store)
    return render_template(INDEX_PAGE, stores=stores, message=message, isShopping = isShopping )
    

@app.route("/register", methods=[GET, POST])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        username = email[:email.find("@")]
        table = None

        if request.form.get("type_options") == BUSINESS:
            table = USER_BUSINESS_TABLE
        else:
            table = USER_CUSTOMER_TABLE

        check_user = db.execute(f"SELECT * FROM {table} WHERE username = :username OR email = :email",
                                    username=username,
                                    email=email)
        if len(check_user) >= 1:
            return render_template(REGISTER_PAGE, form=form, message=USER_EXISTS_MESSAGE)
    
        db.execute(f"INSERT INTO {table} (username, email, hash_pass) VALUES (:username, :email, :hash_pass)",
                    username=username,
                    email=email,
                    hash_pass=generate_password_hash(form.password.data, "sha256"))
        
        return redirect(url_for(LOGIN))
    return render_template(REGISTER_PAGE, form=form)


@app.route("/login", methods=[GET, POST])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        session.clear()

        if request.form.get("type_options") == BUSINESS:
            table = USER_BUSINESS_TABLE
            user_type = BUSINESS
        else:
            table = USER_CUSTOMER_TABLE
            user_type = CUSTOMER

        user = db.execute(f"SELECT * FROM {table} WHERE username = :username", username=form.username.data)
        
        if len(user) != 1 or not check_password_hash(user[0]["hash_pass"], form.password.data):
            return render_template(LOGIN_PAGE, form=form, message=LOGIN_FAILED_MESSAGE)
        
        session["user_id"] = user[0]["id"]
        session["type"] = user_type
        return redirect(url_for(FORM))
    return render_template(LOGIN_PAGE, form=form)

@app.route("/form", methods=[GET, POST])
@login_required
def form():
    if session["type"] == BUSINESS:
        form = BusinessForm()
        type_table = BUSINESS_TABLE
        user_table = USER_BUSINESS_TABLE
        message = BUSINESS_FORM_MESSAGE
    else:
        form = CustomerForm()
        type_table = CUSTOMER_TABLE
        user_table = USER_CUSTOMER_TABLE
        message = CUSTOMER_FORM_MESSAGE

    if form.validate_on_submit():
        if session["type"] == BUSINESS:
            db.execute(f"INSERT INTO business (fiscal_number, activity_sector_id, phone, mobile, name, description, user_id) VALUES (:fiscal, :sector, :phone, :mobile, :name, :desc, :user)",
                fiscal=form.fiscal_number.data, sector=form.activity_sector.data, phone=form.phone.data, mobile=form.mobile.data,
                name=form.name.data, desc=form.description.data, user=session['user_id'])

            business = db.execute(f"SELECT id from business WHERE user_id = {session['user_id']}")
            session["business_id"] = business[0]["id"]
        else:
            db.execute(f"INSERT INTO customers (first_name, last_name, age, user_id) VALUES (:first_name, :last_name, :age, :user)",
                first_name=form.first_name.data, last_name=form.last_name.data, age=form.age.data, user=session['user_id'])
        
        return redirect(url_for(INDEX))
    
    check_user = db.execute(f"SELECT id FROM {type_table} WHERE user_id = {session['user_id']}")

    if not check_user:
        username = db.execute(f"SELECT username from {user_table} WHERE id = {session['user_id']}")
        return render_template(FORM_PAGE, form=form, username=username[0]["username"], message=message)
    else:
        # temporary, business_id will be deprecated
        if session["type"] == BUSINESS:
            business = db.execute(f"SELECT id FROM business WHERE user_id = {session['user_id']}")
            session["business_id"] = business[0]["id"]
        return redirect(url_for(INDEX))


@app.route("/shop/<id>")
def shop(id):
    store = db.execute("SELECT s.id, s.name, s.front_pic, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM stores s LEFT JOIN addresses a ON (a.id = s.address_id) WHERE business_id=:id", id=id)
    if (store[0]["front_pic"] is None or store[0]["front_pic"] == ""):
        picture = IMG_DEFAULT
    else:
        front_pic = store[0]["front_pic"]
        pic = Picture('', front_pic,'')
        pic.name_thumbnail() 
        picture = pic.thumbnail
    store = Store(store[0]["id"],store[0]["name"],picture,store[0]["number"],store[0]["street"],store[0]["zip_code"],store[0]["city"],store[0]["region"],store[0]["country"])
    
    products = []
    for row in db.execute(f"SELECT p.id AS prd_id, p.name AS name, p.description AS description, ps.price AS price, s.id AS store_id, s.name AS store FROM stores AS s INNER JOIN product_store AS ps ON s.id = ps.store_id AND s.id = {id} INNER JOIN products AS p ON ps.product_id = p.id"):
        id = row["prd_id"]
        name = row["name"]
        description = row["description"]
        price = row["price"]
        imgs = db.execute("SELECT file FROM imgs i INNER JOIN  product_img pi ON (i.id = pi.img_id AND pi.product_id = :id)", id = id)
        if len(imgs) >= 1:
            main_img = Picture('', imgs[0]["file"],'')
            main_img.name_thumbnail() 
        else:
            main_img = Picture('', IMG_DEFAULT,IMG_DEFAULT)
        product = Product_shop(id, name, description, main_img.thumbnail, price)
        products.append(product)
    return render_template("shop_products.html", products=products, store=store)


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
            new_store_id = db.execute("INSERT INTO stores (business_id, address_id, name)  VALUES (:id, :address_id, 'new store')", id = session["business_id"], address_id = new_address_id)
            for row in db.execute("SELECT DISTINCT product_id FROM product_store WHERE store_id IN (SELECT id FROM stores WHERE business_id = :id)", id=session["business_id"]):
                db.execute("INSERT INTO product_store (product_id, store_id, price, stock)  VALUES (:product_id, :store_id, 0, 0)", product_id = row["product_id"], store_id=new_store_id)
        else:
            store_id = request.form['submit_button']
            store_name = request.form.get("name_"+store_id)
            db.execute("UPDATE stores SET name=:name WHERE id=:id", name = store_name, id=store_id)
            #store's image update
            if request.files["image_"+store_id]:
                file = request.files["image_"+store_id]
                extension = file.filename.split('.')[1]
                image_name="store_front_pic_"+store_id+"."+extension
                file.save(os.path.join(app.config["IMAGE_UPLOADS"], image_name))
                db.execute("UPDATE stores SET front_pic=:front_pic WHERE id=:id", front_pic = image_name, id=store_id)
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
    for row in db.execute("SELECT * FROM business WHERE id=:id", id=session["business_id"]):
        business.name = row["name"]
        business.description = row["description"]
        business.fiscal_number = row["fiscal_number"]
        business.phone = row["phone"]
        business.mobile = row["mobile"]
    for row in db.execute("SELECT s.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM stores s LEFT JOIN addresses a ON (a.id = s.address_id) WHERE business_id=:id", id=session["business_id"]):
        if (row["front_pic"] is None or row["front_pic"] == ""):
            front_pic = IMG_DEFAULT
        else:
            front_pic = row["front_pic"]
        store = Store(row["id"],row["name"],front_pic,row["number"],row["street"],row["zip_code"],row["city"],row["region"],row["country"])
        business.add_store(store)
    
    return render_template(STORE_PAGE, business =  business)


@app.route("/product", methods=[GET, POST])
@login_required
def product():
    products = []
    hasproduct = False
    for row in db.execute("SELECT DISTINCT p.* FROM products p INNER JOIN product_store ps ON (ps.product_id = p.id) INNER JOIN stores s ON (s.id=ps.store_id) WHERE s.business_id=:id", id=session["business_id"]):
        hasproduct = True
        id = row["id"]
        name = row["name"]
        description = row["description"]
        if row["business_id"]==session["business_id"]:
            isOwner = True
        else:
            isOwner = False
        imgs = db.execute("SELECT file FROM imgs i INNER JOIN  product_img pi ON (i.id = pi.img_id AND pi.product_id = :id)", id = id)
        if len(imgs) >= 1:
            main_img = Picture('', imgs[0]["file"],'')
            main_img.name_thumbnail() 
        else:
            main_img = Picture('', IMG_DEFAULT,IMG_DEFAULT)
        product = Product(id, isOwner, name, description, main_img.thumbnail)
        products.append(product)
    return render_template(PRODUCT_PAGE, products=products, hasproduct = hasproduct)


@app.route("/single_product/<product_id>", methods=[GET, POST])
@login_required
def single_product(product_id):
    if request.method == POST:
        name = request.form.get("name")
        description = request.form.get("description")
        if request.form['submit'] == 'add_product':
            product_id = db.execute("INSERT INTO products(name, description,business_id) VALUES (:name, :description, :business_id)", name=name, description=description, business_id=session["business_id"])
            for row in db.execute("SELECT id FROM stores WHERE business_id = :id", id=session["business_id"]):
                db.execute("INSERT INTO product_store (product_id, store_id, price, stock) VALUES (:product_id, :store_id, 0, 0)", product_id=product_id, store_id=row["id"])
        elif request.form['submit'] == 'edit_product':
            db.execute("UPDATE products SET name=:name, description=:description WHERE id=:id", name=name, description=description, id=product_id)
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
            if (request.files["image_"+img_id]):
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
    product = Product(product_id, '', '', '', '')
    hasimg = False
    maximg = False
    if product_id != 'new':
        for row in db.execute("SELECT * FROM products WHERE id = :id", id=product_id):
            product.name = row["name"]
            product.description = row["description"]
            if row["business_id"] == session["business_id"]:
                isOwner = True
            else:
                isOwner = False
            product.isOwner = isOwner
        #retrieve all product's images
        for row in db.execute("SELECT id, file FROM imgs i INNER JOIN  product_img pi ON (i.id = pi.img_id AND pi.product_id = :id)", id=product_id):
            pic = Picture(row["id"],row["file"],'')
            pic.name_thumbnail() 
            product.add_image(pic)
            hasimg = True
        if len(product.images) == MAX_IMG_PRODUCT:
            maximg = True
    else :
        isOwner = True
    if isOwner:
        return render_template(SINGLE_PRODUCT_PAGE_EDIT, product=product, hasimg = hasimg, maximg = maximg)
    else:
        return render_template(SINGLE_PRODUCT_PAGE, product=product, hasimg = hasimg)


@app.route("/new_product", methods=[GET, POST])
@login_required
def new_product():
    if request.method == POST:
        if request.form['submit'] == 'create_new_product':
            return redirect(url_for("single_product", product_id = 'new'))
        if request.form['submit'] == 'add_existing_product':
            product_id = request.form.get("productChoice")
            for row in db.execute("SELECT s.* FROM stores s WHERE business_id=:id", id=session["business_id"]):
                db.execute("INSERT INTO product_store (product_id, store_id, price, stock) VALUES (:product_id, :store_id, 0, 0)", product_id=product_id, store_id=row["id"])
            return redirect(url_for("single_product_store", product_id = product_id))
    products = []
    hasProduct = False
    
    #retrieve all products that business doesn't own (!business_id in product table) AND that are not selled yet (not in product_store)
    for row in db.execute("SELECT * FROM products WHERE business_id !=:id AND id NOT IN (SELECT product_id FROM product_store WHERE store_id IN (SELECT id FROM stores WHERE business_id=:id))", id = session["business_id"]):
        product = Product(row["id"], False, row["name"], row["description"], "")
        products.append(product)
        hasProduct = True
    return render_template(NEW_PRODUCT_PAGE, products = products, hasProduct = hasProduct)


@app.route("/single_product_store/<product_id>", methods=[GET, POST])
@login_required
def single_product_store(product_id):
    if request.method == POST:
        for row in db.execute("SELECT s.* FROM stores s WHERE business_id=:id", id=session["business_id"]):
            price = request.form.get("price_"+str(row["id"]))
            stock = request.form.get("stock_"+str(row["id"]))
            db.execute("UPDATE product_store SET price=:price, stock=:stock WHERE product_id=:product_id AND store_id=:store_id", price=price, stock=stock, store_id=row["id"], product_id=product_id)
    product = Product(product_id, '', '', '', '')
    for row in db.execute("SELECT * FROM products WHERE id = :id", id=product_id):
        product.name = row["name"]
        product.description = row["description"]
        for row in db.execute("SELECT * FROM product_store WHERE product_id = :id", id=product_id):
            product.add_stock(row["store_id"],row["stock"])
            product.add_price(row["store_id"],row["price"])
    stores = []
    for row in db.execute("SELECT s.* FROM stores s WHERE business_id=:id", id=session["business_id"]):
        store = Store(row["id"],row["name"],'','','','','','','')
        stores.append(store)
    return render_template(SINGLE_PRODUCT_STORE_PAGE, product = product, stores = stores)

@app.route("/add_basket", methods=[GET, POST])
def add_basket():
    if request.method == POST:
        product_id = request.form.get("product_id")
        store_id = request.form.get("store_id")
        new = True
        basket = bm.get_dict()
        for key in basket:
            if key[0] == product_id and key[1] == store_id:
                basket[key] += 1
                new = False
        if new:
            bm.add((product_id,store_id),1)
        #resp = redirect(url_for(INDEX))
        resp = redirect(request.referrer)
        resp.set_cookie("basket", str(bm.get_dict()))
        print("nb article dans le basket : ")
        print (bm)
    return resp

@app.route("/update_quantity_basket", methods=[GET, POST])
def update_quantity_basket():
    if request.method == POST:
        product_id = request.form.get("product_id")
        store_id = request.form.get("store_id")
        basket = bm.get_dict()
        bm.add((product_id,store_id),int(request.form.get("quantity")))
    resp = redirect(url_for(BASKET))
    resp.set_cookie("basket", str(bm.get_dict()))
    return resp

@app.route("/remove_basket", methods=[GET, POST])
def remove_basket():
    if request.method == POST:
        product_id = request.form.get("product_id")
        store_id = request.form.get("store_id")
        basket = bm.get_dict()
        bm.remove((product_id,store_id))
    resp = redirect(url_for(BASKET))
    resp.set_cookie("basket", str(bm.get_dict()))
    return resp

@app.route("/basket", methods=[GET, POST])
def basket():    
    try:
        if session['user_id'] :
            login = True
    except KeyError:
            login = False
    basket = bm.get_dict()
    store_list = bm.get_store_list()
    print(store_list)
    if len(store_list) > 0 :
        full_basket = FullBasket()
        for store_id in store_list:
            store_name = db.execute("SELECT name FROM stores WHERE id =:id", id=store_id)
            new_basket = Basket(store_id, store_name[0]["name"], 0)
            amount = 0
            for key, value in basket.items():
                if key[1] == store_id:
                    product_info = db.execute("SELECT p.name, sp.price, sp.stock FROM products p INNER JOIN product_store sp ON (p.id = sp.product_id AND sp.store_id = :store_id) WHERE p.id = :product_id", store_id = key[1], product_id = key[0])
                    imgs = db.execute("SELECT file FROM imgs i INNER JOIN  product_img pi ON (i.id = pi.img_id AND pi.product_id = :id)", id = key[0])
                    if len(imgs) >= 1:
                        main_img = Picture('', imgs[0]["file"],'')
                        main_img.name_thumbnail() 
                    else:
                        main_img = Picture('', IMG_DEFAULT,IMG_DEFAULT)
                    final_price = float(value) * float(product_info[0]["price"])
                    p = Product_ordered(key[0], product_info[0]["name"], main_img.thumbnail,  product_info[0]["price"], value, final_price, product_info[0]["stock"])
                    new_basket.add_product(p)
                    amount += final_price
            new_basket.amount = amount
            full_basket.add_basket(new_basket)
    else:
        full_basket = False

    #make an order
    if request.method == POST:
        if login:
            orders = []
            for a in full_basket.baskets:
                #to do : replace user_id by customer_id
                order_id = db.execute("INSERT INTO orders (date,amount,status_id,store_id,customer_id)  VALUES (DATE('now') , :amount, 1, :store_id, :customer_id)", store_id = a.store_id, amount=a.amount, customer_id = session['user_id'])
                for b in a.products:
                    db.execute("INSERT INTO order_product (order_id, product_id, quantity, final_price)  VALUES (:order_id , :product_id, :quantity, :price)", order_id = order_id, product_id = b.id, quantity = b.quantity, price = b.final_price)
            bm.empty_basket()  
            full_basket = False

    total_amount = 0
    if full_basket:
        total_amount = bm.total(full_basket)    
    return render_template("basket.html", full_basket = full_basket, amount = total_amount, login = login)


@app.route("/orders", methods=[GET, POST])
@login_required
def order():
    orders = []
    #retrieve all orders not completed (status_id != 4)
    if session["type"] == BUSINESS:
        query = db.execute("SELECT o.id, o.date, o.amount, o.status_id, o.store_id, o.customer_id, sta.name AS status_name FROM orders o INNER JOIN status sta ON (o.status_id = sta.id)  WHERE store_id IN (select id FROM stores WHERE business_id = :id) and status_id != 4", id = session["business_id"])
    if session["type"] == CUSTOMER:
        query = db.execute("SELECT o.id, o.date, o.amount, o.status_id, o.store_id, o.customer_id, sta.name AS status_name FROM orders o INNER JOIN status sta ON (o.status_id = sta.id)  WHERE customer_id = :id and status_id != 4", id = session["user_id"])

    for row in query:
        s = db.execute("SELECT s.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM stores s LEFT JOIN addresses a ON (a.id = s.address_id) WHERE s.id=:id", id=row['store_id'])
        store = Store(s[0]["id"],s[0]["name"],'',s[0]["number"],s[0]["street"],s[0]["zip_code"],s[0]["city"],s[0]["region"],s[0]["country"])
        c = db.execute("SELECT c.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM customers c LEFT JOIN addresses a ON (a.id = c.address_id) WHERE c.id=:id", id=row['customer_id'])
        customer = Customer(c[0]["id"],c[0]["first_name"],c[0]["last_name"],c[0]["number"],c[0]["street"],c[0]["zip_code"],c[0]["city"],c[0]["region"],c[0]["country"])
        order = Order(row["id"], row["date"], row["amount"], row["status_name"], row["status_id"], store, customer)
        orders.append(order)
    return render_template(ORDER_PAGE, orders=orders,  title ="My current orders")


@app.route("/order_details/<order_id>", methods=[GET, POST])
@login_required
def order_details(order_id):
    updateStatusAvailable = False
    status_list = []
    for row in db.execute("SELECT * FROM status"):
        status = Status(row["id"], row["name"], row["description"])
        status_list.append(status)
    if request.method == POST:
        new_status = request.form.get("status")
        db.execute("UPDATE orders SET status_id=:status_id WHERE id=:id", id=order_id, status_id=new_status)
    for row in db.execute("SELECT o.id, o.date, o.amount, o.status_id, o.store_id, o.customer_id, sta.name AS status_name, sto.name AS store_name FROM orders o INNER JOIN status sta ON (o.status_id = sta.id) INNER JOIN stores sto ON (o.store_id = sto.id) WHERE o.id = :id", id = order_id):
        s = db.execute("SELECT s.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM stores s LEFT JOIN addresses a ON (a.id = s.address_id) WHERE s.id=:id", id=row['store_id'])
        store = Store(s[0]["id"],s[0]["name"],'',s[0]["number"],s[0]["street"],s[0]["zip_code"],s[0]["city"],s[0]["region"],s[0]["country"])
        c = db.execute("SELECT c.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM customers c LEFT JOIN addresses a ON (a.id = c.address_id) WHERE c.id=:id", id=row['customer_id'])
        customer = Customer(c[0]["id"],c[0]["first_name"],c[0]["last_name"],c[0]["number"],c[0]["street"],c[0]["zip_code"],c[0]["city"],c[0]["region"],c[0]["country"])
        order = Order(row["id"], row["date"], row["amount"], row["status_name"], row["status_id"], store, customer)
    if session["type"] == BUSINESS:
        if order.status_id != 4:
            updateStatusAvailable = True
    for row in db.execute("SELECT o.*, p.name FROM order_product o LEFT JOIN products p ON (o.product_id = p.id) WHERE order_id = :id", id = order_id):
        product = Product_ordered(row["product_id"], row["name"], '', '', row["quantity"], row["final_price"], '')
        order.add_product(product)
    return render_template(ORDER_DETAILS_PAGE, order = order, status_list = status_list, updateStatusAvailable = updateStatusAvailable)


@app.route("/history")
@login_required
def history():
    orders = []
    #retrieve all completed orders (status_id = 4)
    if session["type"] == BUSINESS:
        query = db.execute("SELECT o.id, o.date, o.amount, o.status_id, o.store_id, o.customer_id, sta.name AS status_name FROM orders o INNER JOIN status sta ON (o.status_id = sta.id)  WHERE store_id IN (select id FROM stores WHERE business_id = :id) and status_id = 4", id = session["business_id"])
    if session["type"] == CUSTOMER:
        query = db.execute("SELECT o.id, o.date, o.amount, o.status_id, o.store_id, o.customer_id, sta.name AS status_name FROM orders o INNER JOIN status sta ON (o.status_id = sta.id)  WHERE customer_id = :id and status_id = 4", id = session["user_id"])
    
    for row in query:
        s = db.execute("SELECT s.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM stores s LEFT JOIN addresses a ON (a.id = s.address_id) WHERE s.id=:id", id=row['store_id'])
        store = Store(s[0]["id"],s[0]["name"],'',s[0]["number"],s[0]["street"],s[0]["zip_code"],s[0]["city"],s[0]["region"],s[0]["country"])
        c = db.execute("SELECT c.*, a.number, a.street, a.zip_code, a.city, a.region, a.country FROM customers c LEFT JOIN addresses a ON (a.id = c.address_id) WHERE c.id=:id", id=row['customer_id'])
        customer = Customer(c[0]["id"],c[0]["first_name"],c[0]["last_name"],c[0]["number"],c[0]["street"],c[0]["zip_code"],c[0]["city"],c[0]["region"],c[0]["country"])
        order = Order(row["id"], row["date"], row["amount"], row["status_name"], row["status_id"], store, customer)
        orders.append(order)
    return render_template(ORDER_PAGE, orders=orders, title = "History (completed orders)")

    
@app.route("/account", methods=[GET, POST])
@login_required
def account():
    customer_form = CustomerAccountForm()
    user_form = UserAccountForm()
    address_form = AddressAccountForm()
    business = BusinessForm()
    message = None

    if business.validate_on_submit():
        db.execute(f"UPDATE business SET fiscal_number = :fiscal_number, phone = :phone, mobile = :mobile, name = :name, description = :description WHERE id = {session['business_id']}",
            fiscal_number=business.fiscal_number.data, phone=business.phone.data, mobile=business.mobile.data,
            name=business.name.data, description=business.description.data)
        message = UPDATE_ACCOUNT_MESSAGE

    if customer_form.validate_on_submit():
        db.execute(f"UPDATE customers SET first_name = :first_name, last_name = :last_name, age = :age WHERE user_id = {session['user_id']}",
            first_name=customer_form.first_name.data, last_name=customer_form.last_name.data, age=customer_form.age.data)
        message = UPDATE_ACCOUNT_MESSAGE
    
    if user_form.validate_on_submit():
        db.execute(f"UPDATE user_customers SET email = :email, hash_pass = :password WHERE id = {session['user_id']}",
            email=user_form.email.data, password=generate_password_hash(user_form.password.data, "sha256"))
        message = UPDATE_ACCOUNT_MESSAGE

    if address_form.validate_on_submit():
        check_address = db.execute(f"SELECT a.* FROM addresses AS a INNER JOIN customers AS c ON a.id = c.address_id AND c.user_id = {session['user_id']}")
        
        if not check_address:
            db.execute(f"INSERT INTO addresses (street, number, zip_code, city, region, country) VALUES (:street, :number, :zip_code, :city, :region, :country)",
                street=address_form.street.data, number=address_form.number.data, zip_code=address_form.zip_code.data,
                city=address_form.city.data, region=address_form.region.data, country=address_form.country.data)

            address_id = db.execute(f"SELECT id FROM addresses WHERE street = :street AND number = :number AND zip_code = :zip_code AND city = :city AND region = :region AND country = :country",
            street=address_form.street.data, number=address_form.number.data, zip_code=address_form.zip_code.data,
            city=address_form.city.data, region=address_form.region.data, country=address_form.country.data)

            db.execute(f"UPDATE customers SET address_id = {address_id[0]['id']} WHERE user_id = {session['user_id']}")
        else:
            address_id = db.execute(f"SELECT address_id FROM customers WHERE user_id = {session['user_id']}")

            db.execute(f"UPDATE addresses SET street = :street, number = :number, zip_code = :zip_code, city = :city, region = :region, country = :country WHERE id = {address_id[0]['address_id']}",
                street=address_form.street.data, number=address_form.number.data, zip_code=address_form.zip_code.data,
                city=address_form.city.data, region=address_form.region.data, country=address_form.country.data)
        message = UPDATE_ACCOUNT_MESSAGE
    
    if session["type"] == BUSINESS:
        query_business = str(db.execute(f"SELECT * FROM business WHERE id = {session['business_id']}"))
        qb = ast.literal_eval(query_business[1:len(query_business)-1])
        field_data = MultiDict()
        field_data.update(qb)
        return render_template(ACCOUNT_PAGE,
            business=BusinessAccountForm(formdata=field_data),
            user_type=session["type"],
            tax_number=field_data.get("fiscal_number")
            )
    else:
        field_data = MultiDict()
        # Customer form data
        query_customer = str(db.execute(f"SELECT first_name, last_name, age FROM customers WHERE user_id = {session['user_id']}"))
        qc = ast.literal_eval(query_customer[1:len(query_customer)-1])
        field_data.update(qc)
        # User form data
        query_user = str(db.execute(f"SELECT email from user_customers WHERE id = {session['user_id']}"))
        qu = ast.literal_eval(query_user[1:len(query_user)-1])
        field_data.update(qu)
        # Address form data
        query_address = db.execute(f"SELECT a.* FROM addresses AS a INNER JOIN customers AS c ON a.id = c.address_id WHERE c.user_id = {session['user_id']}")
        
        if query_address:
            qa = ast.literal_eval(str(query_address)[1:len(str(query_address))-1])
            field_data.update(qa)
    
        return render_template(ACCOUNT_PAGE,
            user_type=session["type"],
            message=message, 
            customer=CustomerAccountForm(formdata=field_data),
            user=UserAccountForm(formdata=field_data),
            address=AddressAccountForm(formdata=field_data)
            )


@app.route("/logout")
@login_required
def logout():
    session.clear()
    bm.empty_basket()
    resp = redirect(url_for(INDEX))
    resp.set_cookie("basket", "", expires=0)
    return resp