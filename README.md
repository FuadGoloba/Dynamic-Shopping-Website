# Web Application Developed in Python(Flask), JavaScript, HTML, & CSS
## KayKaybrand Women's Online clothing store
An online shopping Website developed using Python's web framework (Flask) for back-end.

## Description & Features of Website
This project is a website prototype for my partner's Online Shopping store (KayKaybrand). The website allows users to view products, signup, login, and perform transactions.
Although, currently, no payment gateway has been integrated but there's an option to top up user's wallet during and after registration. I have hosted this web application on Heroku and can be viewed here https://kaykaybrand.herokuapp.com
The main feature of the website is to provide a means for Users to top up their shopping wallet with an amount they would like to shop with.

### Features
- View Products and Catalog: The website is designed such that users can navigate through the pages without signing up or logging in. Here, they can view products, collections, and view carts.
- Register/Login: The webiste has a Login/Register for new and existing customers to create a profile and make changes to their profile. A user can only perform transactions and checkout after Logging in.
- Edit Profile: When logged in, Users can edit profile information, change email address, change password, view orders and update shopping wallet.
- Wallet Top Up: The website currently has no payment gateway integration (looking to integrate soon) but there exists a wallet feature where users need to top up with an amout to shop with. This can be accessed during registration and also in a Logged in User's profile options.
- Modify Cart: Users can add, update, and remove items from cart with and without login. Also, only a logged in user would have their cart items stored even after logging out or being out of session
- Checkout: Users can checkout items in the cart, modify shipping address, contact, and can update wallet should there insufficient balance to complete checkout.
- View Order Summary: The website stores users' order information after completing checkout.

## Software and Project files
### Software Used
- Front-End: HTML, CSS, JavaScript
- Back-End: Flask(Python Web framework), CS50 SQLite for SQL database management
### Project Files
- app.py: The main python program to be run in order to run the server(Flask App). The application contains all routes that accepts requests from the webpage.
- createdb.py: Python code with all the utitlity functions for creating the SQL database. Uses CS50's module of python's inbuilt library sqlite3 as SQL database connector. 
- import_functions.py: Python program with utility functions used in app.py
- E-commerce.db: SQLite database containing 6 tables on products, product_category, users, user_wallet, orders, and cart_item
- requirements.txt: This prescribes the packages on which this app will depend.
- products.csv: CSV file containing all products information to be imported in the SQLite database
- category.csv: CSV file containing product categories to be imported in the SQLite database
- countries.csv: CSV file containing list of all countries.
- templates: This folder contains all the Jinja2 templates to be rendered through the Flask App.
- static: This folder contains the static files i.e. CSS, images, product images, etc.

## How To Run
### Dependencies
- Python 3.xx
- Install all packages in requirements.txt (pip3 install -r requirements.txt)

### Running the application
- Install all application dependencies 
- Run createdb.py to create E-commerce.db database
- To run the server execute the following command, each time:
    $ flask run
    
## Future Improvements
- Include a payment gateway integration
- Include an Admin feature to manage inventory, add products, etc.
- Improve the aesthetics of the webpage
- Optimise code development and eliminate redundancies
- Split app.py into different scripts 

### Video Demo
https://youtu.be/gLt_tKkMSRM
# Dynamic-Shopping-Website
