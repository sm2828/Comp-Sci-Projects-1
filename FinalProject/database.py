import datetime
import hashlib
import sqlite3
import os


DATABASE_NAME = 'coffee_shop.db'

def add_menu_item(name, category, price, quantity):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the new menu item into the database
    cursor.execute('INSERT INTO menu_items (name, category, price, quantity) VALUES (?, ?, ?, ?)',
                   (name, category, price, quantity))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def update_menu_item_quantity(item_name, quantity):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Update the quantity of the menu item in the database
    cursor.execute('UPDATE menu_items SET quantity = ? WHERE name = ?', (quantity, item_name))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def is_valid_user(username, password):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Retrieve the hashed password for the provided username
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # If a result is found and the hashed password matches the provided password,
    # the user is valid
    if result and result[0] == hash_password(password):
        return True
    else:
        return False

def is_username_available(username):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check if the provided username exists in the database
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # If the result is None, the username is available
    return result is None


def create_user(username, password):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Hash the password before storing it in the database
    hashed_password = hash_password(password)

    # Insert the user account into the database
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def hash_password(password):
    # Hash the password using SHA-256 algorithm
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create the table for user accounts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create the table for menu items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # Create the table for user carts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (item_id) REFERENCES menu_items (id)
        )
    ''')

    # Create the table for orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def add_to_cart(user_id, item_id, quantity):
    if quantity <= 0:
        return False, "Invalid quantity. Please enter a positive number."

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check if the item is available in the menu
    cursor.execute('SELECT id FROM menu_items WHERE id = ?', (item_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False, "Item not found in the menu."

    # Check if the item already exists in the user's cart
    cursor.execute('SELECT quantity FROM carts WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    result = cursor.fetchone()

    if result:
        # Update the quantity of the item in the cart
        updated_quantity = result[0] + quantity
        cursor.execute('UPDATE carts SET quantity = ? WHERE user_id = ? AND item_id = ?', (updated_quantity, user_id, item_id))
    else:
        # Add the item to the cart
        cursor.execute('INSERT INTO carts (user_id, item_id, quantity) VALUES (?, ?, ?)', (user_id, item_id, quantity))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    return True, "Item added to cart successfully."

def create_order(user_id, total_price):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the order record into the database
    cursor.execute('INSERT INTO orders (user_id, total_price, order_date) VALUES (?, ?, ?)',
                   (user_id, total_price, datetime.datetime.now()))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def remove_from_cart(user_id, item_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Remove the item from the user's cart
    cursor.execute('DELETE FROM carts WHERE user_id = ? AND item_id = (SELECT id FROM menu_items WHERE name = ?)',
                   (user_id, item_name))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def get_menu_items():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Retrieve menu items from the database
    cursor.execute('SELECT id, name, price, quantity FROM menu_items')  # Include the 'id' column in the query
    menu_items = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return a list of menu items, each represented as a dictionary
    menu = []
    for item in menu_items:
        menu.append({
            'id': item[0],  # Include the 'id' in the dictionary
            'name': item[1],
            'price': item[2],
            'quantity': item[3]
        })

    return menu

if __name__ == '__main__':
    create_tables()
