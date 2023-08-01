from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import database
from database import is_valid_user, create_user

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Sample data structures for testing
menu = {
    'espresso': {'name': 'Espresso', 'price': 2.5, 'quantity': 10},
    'cappuccino': {'name': 'Cappuccino', 'price': 3.0, 'quantity': 8},
    # Add more items to the menu as needed
}

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Route for the root URL
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form['item_name']
    item_price = float(request.form['item_price'])
    quantity = int(request.form['quantity'])

    # Check if the cart already exists in the session, if not, create an empty cart dictionary
    if 'cart' not in session:
        session['cart'] = {}

    # Add the item to the cart or update its quantity if it already exists in the cart
    if item_name in session['cart']:
        session['cart'][item_name]['quantity'] += quantity
    else:
        session['cart'][item_name] = {'price': item_price, 'quantity': quantity}

    # Calculate the total price of items in the cart
    total_price = sum(item['price'] * item['quantity'] for item in session['cart'].values())

    # Store the total price in the session
    session['total_price'] = total_price

    return redirect(url_for('view_menu'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    # Clear the cart and set the total price to 0
    session['cart'] = {}
    session['total_price'] = 0
    flash("Shopping cart cleared.")
    return redirect(url_for('view_menu'))

# Route for user sign-up
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

# Route for user sign-in
@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password for comparison with the hashed password in the database
        hashed_password = hash_password(password)

        # Check if the provided username and password match a user in the database
        if database.is_valid_user(username, hashed_password):
            return f"Welcome, {username}! You are now logged in."

        return "Invalid username or password. Please try again."

    return render_template('signin.html')


@app.route('/menu', methods=['GET', 'POST'])
def view_menu():
    if request.method == 'POST':
        item_key = request.form['item_key']
        quantity = int(request.form['quantity'])

        # Check if the item is available in the menu
        if item_key not in menu:
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
        if item_key in cart:
            cart[item_key]['quantity'] += quantity
        else:
            cart[item_key] = {
                'name': menu[item_key]['name'],
                'price': menu[item_key]['price'],
                'quantity': quantity
            }

        flash(f"{menu[item_key]['name']} added to cart.")
        return redirect(url_for('view_menu'))

    # Calculate the total price of items in the cart
    total_price = sum(item['price'] * item['quantity'] for item in session.get('cart', {}).values())

    return render_template('menu.html', menu=menu, cart=session.get('cart', {}), total_price=total_price)

if __name__ == '__main__':
    app.run(debug=True)
