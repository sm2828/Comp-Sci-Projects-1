import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import hashlib
import database
import datetime
from database import is_valid_user, create_user, get_menu_items, update_menu_item_quantity, add_menu_item

DATABASE_NAME = 'coffee_shop.db'
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

import secrets

# Generate a secure secret key with 32 bytes
secret_key = secrets.token_hex(32)

# Fetch the menu items and their initial quantities from the database
menu = get_menu_items()

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cart', methods=['GET'])
def view_cart():
    # Calculate the total price of items in the cart
    total_price = sum(item['price'] * item['quantity'] for item in session.get('cart', {}).values())

    # Print the cart contents to check if it's populated correctly
    print("Cart Contents:", session.get('cart', {}))

    return render_template('cart.html', cart=session.get('cart', {}), total_price=total_price)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user_id = request.form['user_id']
    item_id = request.form['item_id']
    quantity = int(request.form['quantity'])

    print(f"Received request to add item_id={item_id}, quantity={quantity} to user_id={user_id}")

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check if the item is available in the menu
    cursor.execute('SELECT id, name, price FROM menu_items WHERE id = ?', (item_id,))
    result = cursor.fetchone()
    if not result:
        print(f"Item with item_id={item_id} not found in the menu.")
        conn.close()
        return jsonify({"success": False, "message": "Item not found in the menu."})

    item = {
        "id": result[0],
        "name": result[1],
        "price": result[2],
        "quantity": quantity
    }

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

    # Commit changes
    conn.commit()

    # Get the updated cart contents
    cursor.execute('''
        SELECT menu_items.name, menu_items.price, carts.quantity
        FROM carts
        JOIN menu_items ON carts.item_id = menu_items.id
        WHERE carts.user_id = ?
    ''', (user_id,))
    cart_items = cursor.fetchall()

    # Convert cart items to a list of dictionaries
    cart = []
    total_price = 0
    for cart_item in cart_items:
        cart.append({
            "name": cart_item[0],
            "price": cart_item[1],
            "quantity": cart_item[2]
        })
        total_price += cart_item[1] * cart_item[2]

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Item added to cart successfully.", "cart": cart, "total_price": total_price})

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    # Clear the cart and set the total price to 0
    session['cart'] = {}
    session['total_price'] = 0
    flash("Shopping cart cleared.")
    return redirect(url_for('view_menu'))

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists in the database
        if not database.is_username_available(username):
            return "Username already taken. Please choose a different username."

        # Hash the password before saving to the database
        hashed_password = hash_password(password)

        # Save the user account to the database
        database.create_user(username, hashed_password)
        return "Sign up successful. You can now log in with your username and password."

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password for comparison with the hashed password in the database
        hashed_password = hash_password(password)

        # Check if the provided username and password match a user in the database
        if database.is_valid_user(username, hashed_password):
            # Store the username in the session
            session['username'] = username
            return f"Welcome, {username}! You are now logged in."

        return "Invalid username or password. Please try again."
    

    return render_template('signin.html')

@app.route('/signout')
def sign_out():
    # Clear the username from the session
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/menu', methods=['GET', 'POST'])
def view_menu():
    # Fetch the updated quantity of items from the database
    menu = get_menu_items()

    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])

        # Check if the item is available in the menu
        if item_name not in menu:
            flash("Item not found in the menu.")
            return redirect(url_for('view_menu'))

        # Check if the quantity is valid
        if quantity <= 0:
            flash("Invalid quantity. Please enter a positive number.")
            return redirect(url_for('view_menu'))

        # Initialize the cart if it's not already in the session
        if 'cart' not in session:
            session['cart'] = {}

        # Add the item to the cart or update the quantity if it's already in the cart
        cart = session['cart']
        if item_name in cart:
            cart[item_name]['quantity'] += quantity
        else:
            cart[item_name] = {
                'name': menu[item_name]['name'],
                'price': menu[item_name]['price'],
                'quantity': quantity
            }

        flash(f"{menu[item_name]['name']} added to cart.")
        return redirect(url_for('view_menu'))

    # Calculate the total price of items in the cart
    total_price = sum(item['price'] * item['quantity'] for item in session.get('cart', {}).values())
    print(menu)
    print(session.get('cart', {}))

    return render_template('menu.html', menu=menu, cart=session.get('cart', {}), total_price=total_price)

@app.route('/manager', methods=['GET', 'POST'])
def manager_interface():
    if request.method == 'POST':
        # Check if the form is for adding a new menu item
        if 'add_item' in request.form:
            item_name = request.form['name']
            item_category = request.form['category']
            item_price = float(request.form['price'])
            item_quantity = int(request.form['quantity'])

            # Add the new item to the menu
            add_menu_item(item_name, item_category, item_price, item_quantity)

        # Check if the form is for updating an existing menu item's quantity
        elif 'update_quantity' in request.form:
            item_name = request.form['name']
            item_quantity = int(request.form['quantity'])

            # Update the quantity of the menu item
            update_menu_item_quantity(item_name, item_quantity)

    # Retrieve all menu items to display in the manager interface
    menu_items = get_menu_items()

    return render_template('manager.html', menu_items=menu_items)

def get_customer_orders(manager_id):
    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Fetch customer orders from the database for the given manager ID
    cursor.execute('''
        SELECT orders.id AS order_id, users.username AS customer_username,
               orders.total_price, orders.order_date
        FROM orders
        JOIN users ON orders.user_id = users.id
        WHERE orders.manager_id = ?
        ORDER BY orders.order_date DESC
    ''', (manager_id,))
    orders = cursor.fetchall()

    # Close the connection
    conn.close()

    return orders

def create_order(user_id, manager_id, total_price):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the order record into the database
    cursor.execute('INSERT INTO orders (user_id, total_price, order_date) VALUES (?, ?, ?)',
                   (user_id, total_price, datetime.datetime.now()))

    # Get the ID of the last inserted row (the new order ID)
    order_id = cursor.lastrowid

    # Fetch cart items for the user from the database
    cursor.execute('SELECT item_id, quantity FROM carts WHERE user_id = ?', (user_id,))
    cart_items = cursor.fetchall()

    # Insert the cart items into the order_items table
    for cart_item in cart_items:
        cursor.execute('INSERT INTO order_items (order_id, item_id, price, quantity) VALUES (?, ?, ?, ?)',
                       (order_id, cart_item[0], get_item_price(cart_item[0]), cart_item[1]))

        # Update the menu_items table to reduce the quantity of the item
        cursor.execute('UPDATE menu_items SET quantity = quantity - ? WHERE id = ?', (cart_item[1], cart_item[0]))

    # Delete the items from the user's cart
    cursor.execute('DELETE FROM carts WHERE user_id = ?', (user_id,))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def get_item_price(item_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Retrieve the price of the menu item from the database
    cursor.execute('SELECT price FROM menu_items WHERE id = ?', (item_id,))
    price = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    return price


@app.route('/place_order', methods=['POST'])
def place_order():
    manager_id = session.get('manager_id')
    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty. Add items before placing an order.")
        return redirect(url_for('view_menu'))

    # Calculate the total price of items in the cart
    total_price = sum(item['price'] * item['quantity'] for item in session['cart'].values())

    # Get the user_id of the user who is placing the order
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']  # Replace 'user_id' with the actual key used to store the user ID in the session

    # Create an order record in the database
    create_order(user_id, total_price)

    # Update the inventory quantities and remove items from the cart
    for item_name, cart_item in session['cart'].items():
        quantity = cart_item['quantity']
        update_menu_item_quantity(item_name, quantity)
        remove_from_cart(user_id, item_name)

    # Clear the cart in the session
    session['cart'] = {}

    flash("Order placed successfully. Thank you for shopping with us!")
    return redirect(url_for('view_menu'))


def save_order_to_database(user_id, manager_id, cart_items, total_price):
    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the order details into the orders table
    cursor.execute('INSERT INTO orders (user_id, manager_id, total_price, order_date) VALUES (?, ?, ?, ?)',
                   (user_id, manager_id, total_price, datetime.datetime.now()))

    # Get the ID of the last inserted row (the new order ID)
    order_id = cursor.lastrowid

    # Insert the cart items into the order_items table
    for item_name, item_data in cart_items.items():
        cursor.execute('INSERT INTO order_items (order_id, item_name, price, quantity) VALUES (?, ?, ?, ?)',
                       (order_id, item_name, item_data['price'], item_data['quantity']))

    # Remove the items from the user's cart
    for item_name in cart_items.keys():
        remove_from_cart(user_id, item_name)
        

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def remove_from_cart(item_name):
    # Get the cart items from the session
    cart_items = session.get('cart', {})

    # Remove the item from the cart
    if item_name in cart_items:
        del cart_items[item_name]

    # Update the cart in the session
    session['cart'] = cart_items

@app.route('/manager', methods=['GET', 'POST'])
def manager():
    # Check if the user is logged in
    if 'username' not in session or session['username'] != 'SeanManager':
        # If not logged in or not the manager, redirect to the login page
        return redirect(url_for('sign_in'))

    # Check if the form is submitted (login attempt)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the provided username and password match the manager's account
        if username == 'SeanManager' and password == 'manager':
            # Store the username in the session
            session['username'] = username
        else:
            return "Invalid username or password. Please try again."

    return render_template('manager.html')

@app.route('/manager/orders')
def manager_orders():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Retrieve all customer orders from the database
    cursor.execute('''
        SELECT orders.id, users.username, orders.total_price, orders.order_date
        FROM orders
        JOIN users ON orders.user_id = users.id
    ''')
    orders = cursor.fetchall()

    # Close the connection
    conn.close()

    return render_template('manager_orders.html', orders=orders)

@app.route('/clear_inventory', methods=['POST'])
def clear_inventory():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Execute an SQL query to delete all the menu items from the database
    cursor.execute('DELETE FROM menu_items')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    # Redirect the manager back to the manager interface after clearing the inventory
    return redirect(url_for('manager_interface'))

if __name__ == '__main__':
    database.create_tables()
    app.run(debug=True)
