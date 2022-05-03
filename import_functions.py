import os
import requests
import urllib.parse
import csv

from flask import Flask, redirect, render_template, request, session
from functools import wraps
from create_db import db

def apology(message, code=400):
    """Render message as an apology to user.

        We define a function 'escape' to be scoped inside of apology
        so no other functions will be able to call it
    """
    def escape(s):
        """
        A function defined in apology to replace special characters;
        Escape special characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"), ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


# We create a "LOgin Required Decorator"
# For views thas should only be used for users that are logged in, Incase a user goes to the site and is not logged in
# they should be redirected to the login page.
# Note: A decorator is a function that wraps and replaces another function; but remember to compy the original's function information to the new function
# Use functools.wraps() to handle this for you.
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/logon")
        return f(*args, **kwargs)
    return decorated_function

def eur(value):
    """Format value as EUR."""
    return f"€{value:,.2f}"

# Read list of countries from csv
def  list_of_countries():

    countries = []
    
    # Reading countries from csv file and appending to countries list
    with open("countries.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            countries.append(row["Country"])
            
    return countries

def get_user():
    
    #Get user's address
    user = db.execute("""SELECT * 
                          FROM users
                          WHERE id = ?""",
                          session["user_id"])
    
    return user

def get_cart():
    
    # get user's cart item
    cart = db.execute("""SELECT *
                   FROM cart_item
                   WHERE user_id = ? """,
                   session["user_id"])
    return cart


def get_wallet():
    
    user_wallet = db.execute("""SELECT * 
                             FROM user_wallet
                             WHERE user_id = ?""",
                             session["user_id"])
    
    return user_wallet

