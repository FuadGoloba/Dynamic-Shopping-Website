from crypt import methods
import os
import csv
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import *
import dateutil.parser


from import_functions import apology, login_required, eur, list_of_countries, get_user, get_cart, get_wallet
from create_db import db


# Configure application
app = Flask(__name__)

#In order to use session in flask you need to set the secret key in your application settings. 
# secret key is a random key used to encrypt your cookies and save send them to the browser.
# The secret key is needed to keep the client-side sessions secure.
# Secret Key is used to protect user session data in flask
app.config["SECRET_KEY"] = "random string"

# Note- Response Caching reduces the number of requests a client or proxy makes to a web server
# Also reduces the amount of work the web server performs to generate a response
# Ensure templates are auto-reloaded - Disabling caching of responses;
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configuring jinja with a Custom filter, eur, a function (defined in import_functions.py) that makes it easier to format values as USDollars
app.jinja_env.filters["eur"] = eur

# Configuring Flask to store sessions on local filesystem as opposed to storing them inside of (digitally signed) cookies which is Flask's default.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.after_request
def after_request(response):
    """Ensuring responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Converting to a date time format to use in Jinja
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date=dateutil.parser.parse(date)
    native = date.replace(tzinfo=None)
    format = """%A %d, %b %Y"""
    return native.strftime(format)


@app.route("/", methods=["GET", "POST"])
def index():
    
    """ Show Homepage and featured collections"""
    
    
    # Forget any user_id
    #session.clear()
    
    error = None
    if request.method == "POST":

        #Query database for username or password entered by customer 
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Check password
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = 'Invalid Credentials'
            return render_template("logon.html",error=error)
            #return apology("Username and password do not corrspond to any account at KayKay")

        # If the account is validated
        session["user_id"] = rows[0]["id"]
        session["first_name"] = rows[0]["first_name"]
        session["last_name"] = rows[0]["last_name"]
        session["email"] = rows[0]["email"]
        
        # Query for logged in user cart item
        cart = get_cart()
        
        if "cart" not in session:
            session["cart"] = {}
        
        # Update user cart on webpage
        for item in cart:
            product_id = str(item["product_id"])
            quantity = item["quantity"]
            print(product_id, type(product_id))
            
            session["cart"][product_id] = quantity
            
            
        # Redirect user to website homepage
        flash("Logged in")
        return redirect("/")
    
    else:
        return render_template("index.html")

# @app.route("/search")
# def search():
    
#     return render_template("search.html")

# @app.route("/searchItem", methods = ["GET", "POST"])
# def searchItem():
    
#     q = request.args.get("q")
#     if q:
#         products = db.execute("""SELECT *
#                               FROM products
#                               WHERE name
#                               LIKE ?
#                               LIMIT 20""",
#                               "%" + q + "%")
#     else:
#         products = []
        
#     return jsonify(products)

@app.route("/catalog", methods = ["GET", "POST"])
def catalog():
    
    """Show all products page and ability to view page by sort options"""
    
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
    
@app.route("/addtocart", methods=["GET", "POST"])
def addToCart():
    
    """Idea is to get the id of the product the user selected and update
    the cart icon to 1, 2, 3, etc and redirect the user back to the product page 
    to continue shopping. 
    NOte: A situation where the user isn't logged in, we use the user's session
    to monitor its cart items.
    But where the user is logged in from the start, we store the user's cart in the cart db (Might not need this if I plan to use the session to monitor user's cart. Will just have to remove the item on checkout)
    
    Note: This function will only update cart number (i.e increase). Another route will be created to remove from cart"""
    # Creating a dctionary to store the cart items and qty of a user's product in session without login in
    if "cart" not in session:
        session["cart"] = {}
    
    
    # Get the id of the product the user has sent to the server
    id = request.args.get("id")
    
    # Map the product and the quantity selected as a key-value pair and send to the server via post in the dictionary
    if request.method == "POST":
        qty = request.form.get("qty")
        if qty:
            if id not in session["cart"]:
                #session["qty"].append(qty)
                session["cart"][id] = int(qty)
            else:
                session["cart"][id] += int(qty)
    
    
    #print(session["cart"])
    #print(session["qty"])
    #flash("Added")
    return redirect("/catalog")


@app.route("/updateCart", methods=["GET", "POST"])
def updateCart():
    
    """ Update cart """
    
    id = request.args.get("id")
    
    if request.method == "POST":
        qty = request.form.get("qty")
        print(qty, type(qty))
        if qty == "0":
            return removeCartItem()
        if id and qty:
            session["cart"][id] = int(qty)
            
    #print(session["cart"])
            
    return redirect("/cart")


@app.route("/removeItem")
def removeCartItem():
    
    id = request.args.get("id")
    
    if id:
        del session["cart"][id]
        if session["user_id"] != 0:
            # To clear product from user's cart db if user removes product from his cart on webpage
            db.execute(""" DELETE 
                    FROM cart_item
                    WHERE product_id = ?
                    AND user_id = ?""",
                    id,session["user_id"])

    
    return redirect("/cart")

@app.route("/cart")
def cart():
    
    """"""
    
    # Querying the products tabe for products in the user's session cart
    try:
        products = db.execute("""SELECT *
                          FROM products
                          WHERE id in (?)
                          """,list(session["cart"].keys()))
    except:
        products = []

    # Create a dictionary of product id to qty in a user's session 
    #id_qty = dict(zip(session["cart"],session["qty"])) 
     
    subtotal = 0
    # CReating a key-value pair of product id to quantity for each product queried from the products 
    for product in products:
        q = str(product["id"])
        print(q, type(q))
        print(session["cart"][q])
        
        # check that the product id exists in the user's session dictionary of {id:qty}
        if q in session["cart"]:
            product["qty"] = session["cart"][q]
            
        # Calculating Total cost of each product in the cart    
        product["total"] = product["price"] * int(product["qty"])
        
        # Calculating sub-total for all products in cart
        subtotal += product["total"]
        
    
        
        # forcing a user session (not logged in) to 0
        try:
            if not session["user_id"]:
                session["user_id"] = 0    
        except:
            session["user_id"] = 0
        
        # Get user info
        user = get_user()
        
        # Get user's cart
        carts = get_cart()
        
        print(carts)
        
        # Check that a logged in user session exists
        if len(user) != 0:
            
            
            # if user's cart is empty, or user is adding this prpoduct to cart for the first time; then insert the product to user's cart in DB
            if len(carts) == 0 or product["id"] not in [cart["product_id"] for cart in carts]:
                db.execute("""INSERT INTO cart_item
                        (user_id, product_id, quantity, total)
                        VALUES (?,?,?,?)""",
                        user[0]["id"], product["id"], product["qty"],product["total"])
             
            # User cart is not empty and user has products already in the cart DB, then update should the user update qty on that product   
            else:
                db.execute("""UPDATE cart_item
                           SET quantity = ?, total = ?
                           WHERE user_id = ?
                           AND product_id = ?""",
                           product["qty"],product["total"],user[0]["id"],product["id"])
                
    # Update user's total        
    session["total"] = subtotal
        
    return render_template("cart.html",products=products, subtotal=subtotal)


@app.route("/logon")
def logon():
    
    return render_template("/logon.html")


@app.route("/logout")
def logout():

    # clear user session
    session.clear()

    # Redirect to homepage
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    # Get list of countries    
    countries = list_of_countries()
            
    if request.method == 'POST':
        
        email = request.form.get("email")
        password = request.form.get("password")
        first_name = request.form.get("first_name").capitalize()
        last_name = request.form.get("last_name").capitalize()
        phone = request.form.get("phone")
        address_1 = request.form.get("address_1")
        address_2 = request.form.get("address_2")
        city = request.form.get("city").capitalize()
        state = request.form.get("state").capitalize()
        country = request.form.get("country")
        mom_maiden_name = request.form.get("question_1").capitalize()
        born_city = request.form.get("question_2").capitalize()
        wallet = request.form.get("wallet")
        
        # Query user info
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        
        error = None
        if password != request.form.get("repeat-password"):
            error = "Passwords don't match"
            return render_template("register.html", error=error, countries=countries)
        
        if email in [row["email"] for row in rows]:
            error = "E-mail already exists"
            return render_template("register.html", error=error,countries=countries)
        
        # Register user into the  db
        #try:
        db.execute("""INSERT INTO users 
                       (hash, first_name, last_name, email, address_1, address_2, city, state, country, phone, mom_maiden_name, born_city)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                       generate_password_hash(password),first_name,last_name,email,address_1,address_2,city,state,country,phone,mom_maiden_name,born_city)
        
        # Getting all users count 
        all_user = db.execute("SELECT * FROM users")
        # Updating user wallet at registration
        db.execute("""INSERT INTO user_wallet
                   (wallet)
                   VALUES (?)""",
                    wallet)
        
        flash("Registered successfully! You may now log in with your details")
        return redirect("/logon")
    
    else:
        
        return render_template("register.html",countries=countries)
    
    
@app.route("/passwordReset", methods=["GET", "POST"])
def passwordReset():
    
    if request.method == "POST":
        
        email = request.form.get("email")
        mom_maiden_name = request.form.get("question_1")
        born_city = request.form.get("question_2")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirmation")
        
        rows = db.execute(""" SELECT * 
                         FROM users
                         WHERE email = ? 
                         AND mom_maiden_name = ?
                         AND born_city = ?""",
                         email,mom_maiden_name,born_city)
        
        # Check that the user exists in the database
        error = None
        if len(rows) != 1:
            error = 'Invalid Credentials, could not reset password'
            return render_template("logon.html",error=error)
        
        else:
            if new_password != confirm_password:
                error = "Passwords don't match, could not reset password"
                return render_template("passwordReset.html",error=error)
            
            else:
                # Update user;s password 
                db.execute("""UPDATE users
                        SET hash = ?
                        where email = ?""",
                        generate_password_hash(new_password),email)
                
                flash("Password Reset successful")
                return redirect("/logon")
            
    return render_template("passwordReset.html")


@app.route("/profile")
def profile():
    
    return render_template("profile.html")

@app.route("/account")
def account():
    
    return render_template("account.html")

@app.route("/changePassword", methods = ["GET", "POST"])
def changePassword():
    
    if request.method == "POST":
        
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirmation")
        
        # Query user info
        rows = get_user()
        
        # Check that the user exists in the database
        error = None
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"],old_password):
            error = "Current password is incorrect, could not update password"
            return render_template("changePassword.html",error=error)
        
        elif old_password == new_password:
            error = "New password must be different"
            return render_template("changePassword.html",error=error)
            
        else:
            if new_password != confirm_password:
                error = "Passwords don't match, could not update password"
                return render_template("changePassword.html.html",error=error)
            
            else:
                # Update user;s password 
                db.execute("""UPDATE users
                        SET hash = ?
                        where email = ?""",
                        generate_password_hash(new_password),session["email"])
                
                flash("Password Change successful")
                return redirect("/profile")
        
    
    return render_template("changePassword.html")

@app.route("/changeEmail", methods = ["GET", "POST"])
def changeEmail():
    
    if request.method == "POST":
        
        new_email = request.form.get("new_email")
        
        rows = db.execute(""" SELECT * 
                         FROM users""")
        
        user_row = get_user()
        
        error = None
        # Check that user's password is correct
        if len(user_row) != 1 or not check_password_hash(user_row[0]["hash"],request.form.get("password")):
            error = "Password is incorrect, Cannot update E-mail address"
            return render_template("changeEmail.html", error=error)
        
        if new_email in [row["email"] for row in rows]:
            error = "E-mail already exists, Use a different e-mail address"
            return render_template("changeEmail.html", error=error)
        
        if new_email != request.form.get("confirmation"):
            error = "E-mail's don't match"
            return render_template("changeEmail.html", error=error)
        
        # Update user's new email in DB
        db.execute("""UPDATE users
                   SET email = ?
                   WHERE id = ?
                   """,
                   new_email,session["user_id"])
        # Update user's session email in front end
        session["email"] = new_email
        
        flash("Email Change successful")
        return redirect("/profile")
        
    
    return render_template("changeEmail.html")

@app.route("/address")
def address():
    
    # calling function to query user info
    user_info = get_user()
        
    return render_template("address.html", user_info=user_info)

@app.route("/changeAddress", methods = ["GET", "POST"])
def changeAddress():
    
    # Get list of countries to render
    countries = list_of_countries()
    
    # Update user's address information
    if request.method == "POST":
        
        db.execute("""UPDATE users
                   SET address_1 = ?, address_2 = ?, city = ?, state = ?, country = ?, phone = ?
                   WHERE id = ?""",
                   request.form.get("address_1"), request.form.get("address_2"), request.form.get("city"), request.form.get("state"), request.form.get("country"),request.form.get("phone"),
                   session["user_id"])
        
        return redirect("/profile")
    
    return render_template("changeAddress.html", countries=countries)
    
    
@app.route("/checkout", methods = ["GET", "POST"])
@login_required
def checkout():
    
    user = get_user()
    
    user_wallet = get_wallet()
    
    # products = db.execute("""SELECT *
    #                       FROM products
    #                       WHERE id in (?)
    #                       """,list(session["cart"].keys()))
    
    products = db.execute("""SELECT cart_item.quantity, cart_item.total, products.name, products.desc, products.image
                          FROM cart_item
                          JOIN products
                          ON products.id = cart_item.product_id
                          WHERE cart_item.user_id = ?""",
                          session["user_id"])
    #print(products)
    
    return render_template("checkout.html", user=user, user_wallet=user_wallet,products=products)
print(checkout)
 
@app.route("/processOrder")
def processOrder():
    
    # Get user wallet info
    user_wallet = get_wallet()
    
    # Ensure that user has enough in wallet to clear cart items
    if session["total"] > user_wallet[0]["wallet"]:
        
        flash("Insufficient balance in Wallet")
        return redirect("/updateWallet")
    
    # Update user wallet balance
    balance = user_wallet[0]["wallet"] - session["total"]
    db.execute("""UPDATE user_wallet
               SET wallet = ?
               WHERE user_id = ?""",
               balance, session["user_id"])  
    
    # Inserting final cart items into orders table to process order
    cart = get_cart()
    for item in cart:
    
        db.execute("""INSERT INTO orders
                (user_id, product_id, quantity, total)
                VALUES(?,?,?,?)""",
                session["user_id"], item["product_id"], item["quantity"], item["total"])
        
    # Deleting items from users cart after processing order
    session["cart"] = {}
    db.execute("""DELETE 
               FROM cart_item
               WHERE user_id = ?""",
               session["user_id"])  
    
    return render_template("processOrder.html")


@app.route("/order", methods=["GET","POST"])
def order():
    
    user_order = db.execute("""SELECT 
                        products.image, orders.product_id, SUM(orders.total) AS total, DATE(orders.created_at) AS created_date
                        FROM orders
                        JOIN products
                        ON orders.product_id = products.id
                        WHERE user_id = ?
                        GROUP BY created_date""",
                        session["user_id"])
    
    return render_template("order.html", user_order=user_order)


@app.route("/viewOrder", methods = ["GET", "POST"])
def viewOrder():
    
    order_date = request.args.get("date")
    
    order =  db.execute("""SELECT 
                        products.image, products.name, products.desc, orders.quantity, orders.product_id, orders.total, DATE(orders.created_at) AS created_date
                        FROM orders
                        JOIN products
                        ON orders.product_id = products.id
                        WHERE user_id = ?
                        AND created_date = ?""",
                        session["user_id"], order_date)
    
    print(session["user_id"])
    print(order_date)
        
    return render_template("viewOrder.html", order=order)

print(viewOrder)

@app.route("/updateWallet", methods = ["GET","POST"])
def updateWallet():
    
    user_wallet = get_wallet()
    
    if request.method == "POST":
        
        wallet = user_wallet[0]["wallet"] + float(request.form.get("wallet"))
        
        db.execute("""UPDATE user_wallet
                   SET wallet = ?
                   WHERE user_id = ?""",
                   wallet, session["user_id"])
        
        return redirect("/updateWallet")
        
    
    return render_template("updateWallet.html", user_wallet=user_wallet[0])