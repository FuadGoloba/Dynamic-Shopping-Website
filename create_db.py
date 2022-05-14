from cs50 import SQL
import csv

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///E-commerce.db")

# Creating Tables

# create customers table to hold customers' information
def users():

    users_table = """CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY NOT NULL,
    hash TEXT NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    address_1 TEXT NOT NULL,
    address_2 TEXT NOT NULL,
    city VARCHAR NOT NULL,
    state VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    phone VARCHAR NOT NULL,
    mom_maiden_name VARCHAR NOT NULL,
    born_city VARCHAR NOT NULL)
    """
    db.execute("DROP TABLE IF EXISTS users")
    db.execute(users_table)
    db.execute("""CREATE UNIQUE INDEX email ON users (email)""")

# Create user_payment table to store customers' cash availability details
# Note: It is assumed that customers recharge their account on the site in order to make payments
def user_wallet():

    user_wallet_table = """CREATE TABLE IF NOT EXISTS user_wallet
    (user_id INTEGER PRIMARY KEY NOT NULL,
    wallet NUMERIC NOT NULL 
    )"""

    #FOREIGN KEY(user_id) REFERENCES users(id)

    db.execute("DROP TABLE IF EXISTS user_wallet")
    db.execute(user_wallet_table)

# CReate produc_category table to store different product categories
def product_category():

    product_category_table = """CREATE TABLE IF NOT EXISTS product_category
    (id INTEGER NOT NULL,
    name TEXT NOT NULL,
    desc TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id))
    """
    db.execute("DROP TABLE IF EXISTS product_category")
    db.execute(product_category_table)

    with open('category.csv', 'r') as file:

        reader = csv.DictReader(file)
        for row in reader:
            id = int(row['id'])
            name = row['name']
            desc = row['desc']

            try:
                db.execute("""INSERT INTO product_category
                (id, name, desc) VALUES(?,?,?)""",
                id,name,desc)

                msg = f"Product category {name} added successfully"
            except:
                msg = f"Error occured while adding {name}"
    
            print(msg)

# create product_inventory table to track inventory of products
def product_inventory():

    product_inventory_table = """CREATE TABLE IF NOT EXISTS product_inventory
    (id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
    )"""

    db.execute("DROP TABLE IF EXISTS product_inventory")
    #db.execute(product_inventory_table)

# create products table 
def products():

    products_table = """CREATE TABLE IF NOT EXISTS products
    (id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    desc TEXT NOT NULL,
    image TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    price DECIMAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id),
    FOREIGN KEY(category_id) REFERENCES product_category(id)
    )"""

    db.execute("DROP TABLE IF EXISTS products")
    db.execute(products_table)

    # Reading products info from csv file
    with open("products.csv", 'r') as file:

        reader = csv.DictReader(file)
        for row in reader:
            name = row['name']
            desc = row['desc']
            image = row['image']
            quantity = int(row['quantity'])
            category_id = int(row['category_id'])
            price = float(row['price'])

            try:
                db.execute("""INSERT INTO products
                (name,desc,image,quantity,category_id,price) VALUES(?,?,?,?,?,?)""",
                name,desc,image,quantity,category_id,price)

                msg = f"product {name} added successfully"
            except:
                msg = f"Error occured while adding {name}"

            print(msg)

# Create cart_item table to track users' cart
def cart_item():

    cart_item_table = """CREATE TABLE IF NOT EXISTS cart_item
    (user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total DECIMAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
    )"""

    db.execute("DROP TABLE IF EXISTS cart_item")
    db.execute(cart_item_table)


# Create orders table to track user's total orders

def orders():

    orders_table = """CREATE TABLE IF NOT EXISTS orders
    (user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total DECIMAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
    FOREIGN KEY(product_id) REFERENCES products(id)
    )"""

    db.execute("DROP TABLE IF EXISTS orders")
    db.execute(orders_table)

def main():
    users()
    user_wallet()
    #product_category()
    #product_inventory()
    #products()
    #cart_item()
    orders()

if __name__ == "__main__":
    main()