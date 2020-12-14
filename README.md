# local

**local** is a web platform where only local businesses can sell their products online and show themselves to a possible more customers rather than just their locals and neighbors.
From catering trade to fruit shops or bakeries to specialized businesses and traditional product sellers all have a space on local.
Where your local products are accessible to everyone.

## Motivation

This project is a consequence of CS50 course to develop a software from scratch for its final project.
The idea was to build a web based app for small businesses where they have a platform to sell their products beside their usual
local customers.
From a customer point of view they can find more products that are not accessible in big supermarkets and buy more local in a easier way.

## Version

`1.0.0`

* As s **Business** you can:
    * register;
    * log in;
    * create a business (register your activity on **local**);
    * edit your account info;
    * add stores;
    * add products;
    * check orders received;

* As a **Customer** you can:
    * register;
    * log in;
    * edit your account info;
    * add products to basket;
    * buy products;
   
## Screenshots

[Add some screenshots of the app, max 3]

## Tech/framework used:

**local** was built with:

* Flask - as a web application framework;
* Bootstrap - to views styling;
* Sqlite3 - database;

## Improvements:

We hope this `1.0.0` version is the first of a possible future real application.

* Filter stores by location or category
* Apply promo on product's prices
* Send email notification when order's status change
* Apply a new design

## Credits

This projects was an idea of two CS50 students who met online and after a couple of messages decided to start this final project together, they are:

* [@JadeRebecca](https://github.com/JadeRebecca)
* [@jopijuco](https://github.com/jopijuco)

## License

MIT License



## How to launch application

1. Check that you have Python installed
2. Clone the code: `git clone https://github.com/.....
3. Run command prompt in the folder and run these set of command to install Flask and other dependencies :
- pip install flask 
- pip install cs50  
- pip install requests 
- pip install Flask-Session 
- pip install Flask-WTF
- pip install email-validator
- pip install pillow 
4. Once installed run command `set FLASK_APP=application.py`
5. Then run `python -m flask run` to run the app
5. Click on the URL displayed on your command prompt `http://:xxx.x.x.x:xxxx/`
6. You are ready to go!