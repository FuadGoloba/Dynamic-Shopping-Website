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

# Configuring jinja with a Custom filter, usd, a function (defined in helpers.py) that makes it easier to format values as USDollars
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

@app.route("/")
def index():
    
    return render_template("layout.html")

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