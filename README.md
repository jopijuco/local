# CS50 Final Project - local platform

The project is a webapp where business can create online shop for local customers.
This first version is made with a simple and clean design, and focus on the main functionality that locals sellers needs, specially during this particular context.


Technologies used:

- Flask
- sqlite3
- Bootstrap

## How the website works?

Any user can explore the website without registering, and enter in any shop to see the product's catalogue.
To buy some products, user must be register and loggued as a customer.
The user can register either as business or customer. During registration you need to enter these fields:

- Email
- Name
- Password: any constraint?


### Customer View

As a Customer, you can start your shopping without beeing logged, but you must be logged as a customer to finalize your order.
When accessing the basket page, you can finalize the order.

#### Shopping
to complete

#### Orders
to complete

#### Account
to complete

### Business View

Business registration allows you to access personnal business area, where you can manage your store(s), your product(s) and your order(s).

#### Stores
A Business has at least one store
When the order's status is completed, you can't see it in the orders tab anymore, you must go to the history tab to find it.

#### Products
A Business can create a new product and add it to all of its stores. In this case, the business is the owner of this product and is able to modify product's name, description and images.
A Business can also add an existing product to his store(s). In this case, it's not the product's owner so it can't modify product's name, description and images.
When a Business add a product to his stores (by creating a new one or picking an existing), he must enter the price and the quantity for each of his store.

#### Orders

### Routing

For all businesses and customer specific pages, each route checks if the user is authenticated. 
So for example a regular user (not logged in) or a customer cannot enter /xxx/xxx/ route (write an example). 

### Sessions

The webpage uses sessions to confirm that user is registered. 
To complete...

### Database

Database stores all users, business and orders data. 
Add a schema of the DB?

## Possible improvements

This version is the first of a possible future real application. Possible improvements:

- Filter stores by location or category
- Apply promo on product's prices
- Send email notification when order's status change
- Apply a new design

## How to launch application

1. Check that you have Python installed
2. Clone the code: `git clone https://github.com/.....
3. Run command prompt in the folder and run these set of command to install Flask and other dependencies :
- pip install flask 
- pip install cs50  
- pip install requests 
- pip install Flask-Session 
- pip install pillow 
4. Once installed run command `set FLASK_APP=application.py`
5. Then run `python -m flask run` to run the app
5. Click on the URL displayed on your command prompt `http://:xxx.x.x.x:xxxx/`
6. You are ready to go!

