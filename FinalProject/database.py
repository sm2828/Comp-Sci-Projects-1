import hashlib
import sqlite3
import os


DATABASE_NAME = 'coffee_shop.db'

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

if __name__ == '__main__':
    create_tables()
