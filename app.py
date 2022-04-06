import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from import_functions import apology, login_required, eur
from create_db import db


# Configure application
app = Flask(__name__)

#In order to use session in flask you need to set the secret key in your application settings. 
# secret key is a random key used to encrypt your cookies and save send them to the browser.
# The secret key is needed to keep the client-side sessions secure.
# Secret Key is used to protect user session data in flask
#app.config["SECRET_KEY"] = "656583ce67c0554a1f0b67a7820f0833"

# Note- Response Caching reduces the number of requests a client or proxy makes to a web server
# Also reduces the amount of work the web server performs to generate a response
# Ensure templates are auto-reloaded - Disabling caching of responses;
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configuring jinja with a Custom filter, eur, a function (defined in import_functions.py) that makes it easier to format values as USDollars
app.jinja_env.filters["eur"] = eur

# Configuring Flask to store sessions on local filesystem as opposed to storing them inside of (digitally signed) cookies which is Flask's default.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#Session(app)


@app.after_request
def after_request(response):
    """Ensuring responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    
    """ Show Homepage and featured collections"""
    
    #feature_img = db.execute("SELECT image FROM products limit 3")
    #feature_img = db.execute("""SELECT 
    #                         product_category.name AS category_name, products.image AS image, products.name AS name, products.price AS price 
    #                         FROM products 
    #                         JOIN product_category 
    #                         ON product_category.id = products.category_id 
    #                         GROUP BY products.category_id 
    #                         LIMIT 4""")
    #print(feature_img)
    
    return render_template("index.html")
    #return render_template("index.html",feature_img=feature_img)

#print(index())

@app.route("/catalog", methods = ["GET", "POST"])
def catalog():
    
    """Show all products page"""
    
    # Create a list of sort options
    sort_option = ["Product, A-Z", "Product, Z-A", "Price, Lowest", "Price, Highest"]
    
    # Sort alphabetically A-Z
    productsA_Z = db.execute(""" SELECT name, image, price
                              FROM products
                              ORDER BY name ASC
                              """)
    
    # Sort alphabetically Z-A
    productsZ_A = db.execute(""" SELECT name, image, price
                              FROM products
                              ORDER BY name DESC
                              """)
    
    # Sort by Lowest price
    productsLowest_price = db.execute(""" SELECT name, image, price
                              FROM products
                              ORDER BY price ASC
                              """)
    
    # Sort by Highest Proice
    productsHighest_price = db.execute(""" SELECT name, image, price
                              FROM products
                              ORDER BY price DESC
                              """)
    
    # If the user selects any of the sort options, render the respective option to the pproducts page
    if request.method == "POST":
        
        if request.form.get("sort_by") == "Product, A-Z":
            return render_template("catalog.html",sort_option=sort_option,products=productsA_Z)
        elif request.form.get("sort_by") == "Product, Z-A":
            return render_template("catalog.html",sort_option=sort_option,products=productsZ_A)
        elif request.form.get("sort_by") == "Price, Lowest":
            return render_template("catalog.html",products=productsLowest_price,sort_option=sort_option)
        elif request.form.get("sort_by") == "Price, Highest":
            return render_template("catalog.html",products=productsHighest_price,sort_option=sort_option)
    
    
    return render_template("catalog.html",products=productsA_Z,sort_option=sort_option)
    #return render_template("catalog.html",products=products,sort_option=sort_option)
    

@app.route("/productDetail")
def productDetail():
    
    """ Show single product description based on user's selection """
    
    # Get the name of the product for which detail to show (This name is gotten from the url of the product selected)
    product_name = request.args.get("name")
    
    # Query to get the product detail from products table
    product_detail = db.execute("""SELECT * 
                                FROM products
                                WHERE name = ?
                                """, product_name)
    
    # Query to get related products
    related_products = db.execute("""SELECT * 
                                  FROM products
                                  WHERE category_id = (SELECT category_id
                                                       FROM products
                                                       WHERE name = ?)
                                  AND name != ?
                                  LIMIT 4
                                  """,product_name,product_name)
    # Get a range of sizes for the products
    sizes = [i for i in range(6,21,2)]
    
    return render_template("productDetail.html", sizes=sizes, product_detail=product_detail, related_products=related_products)
    
@app.route("/addtocart")
def addToCart():
    
    #flash("Added")
    return redirect("/")


@app.route("/cart")
def Cart():
    return 
    

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()
    
    if request.method == "POST":

        #Query database for username or password entered by customer 
        rows = db.execute("SELECT * FROM users WHERE username = ? OR WHERE email = ?", request.form.get("username"), request.form.get("email"))


        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Username and password do not corrspond to any account at KayKay")

        # If the account is validated
        session["user_id"] = rows[0]["id"]

        # Redirect user to website homepage
        flash("Logged in")
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # clear user session
    session.clear()

    # Redirect to homepage
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    return