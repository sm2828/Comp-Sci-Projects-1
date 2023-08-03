Flask Coffee Shop Project
This is a simple online coffee shop application developed using Flask. It allows customers to create an account, view the menu, add items to their cart, and place orders. Additionally, coffee shop managers can add new items, update quantities, and view customer orders.

Getting Started
Follow the steps below to set up and run the Flask Coffee Shop application on your local machine.

Prerequisites
Python 3.x: Make sure you have Python 3.x installed on your system. If you don't have it, you can download it from the official Python website: https://www.python.org/downloads/

Virtual Environment (Optional but Recommended): It is recommended to set up a virtual environment to manage project dependencies. You can use virtualenv or venv for this purpose.

Installation
Clone the project repository to your local machine.

(Optional but Recommended) Create a virtual environment in the project directory:

# If using virtualenv
virtualenv flaskenv

# If using venv (Python 3.3+)
python3 -m venv flaskenv


Activate the virtual environment:

On Windows:
flaskenv\Scripts\activate

On macOS/Linux:
source flaskenv/bin/activate

Install the project dependencies (Flask and SQLite3):
pip install flask


Running the Application
Ensure that the virtual environment is activated.

In the project root directory, run the following command:
python app.py

The Flask development server will start, and you should see output similar to the following:
* Serving Flask app 'app'
* Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
Use a production WSGI server instead.
* Running on http://127.0.0.1:5000/

Open your web browser and go to http://127.0.0.1:5000/ to access the home page of the Coffee Shop application.

Usage
Home Page: http://127.0.0.1:5000/ - This is the landing page of the Coffee Shop application, where you can find a button to view the menu.

Menu Page: http://127.0.0.1:5000/menu - Click on the "View Menu" button on the home page to access the Coffee Shop menu, where you can see available coffee and food items along with their prices and quantities.

Sign Up Page: http://127.0.0.1:5000/signup - To create a new account, click on the "Sign Up" button on the home page and fill out the sign-up form.

Sign In Page: http://127.0.0.1:5000/signin - If you already have an account, click on the "Sign In" button on the home page and provide your credentials to log in.

Manager Functionality: Manager actions such as adding new items to the menu, updating item quantities, and viewing customer orders are not yet implemented in this version of the application.

Development Notes
The project uses SQLite3 as the database to store user accounts and menu data. This is suitable for development and testing purposes, but in a production environment, you may want to use a more robust database system.

The application uses basic CSS styles to improve the appearance of the pages. You can further enhance the frontend by adding more styles and customizations.

This application is designed for educational purposes and as a starting point for building more complex web applications. Feel free to expand the features and functionalities according to your requirements.

License
This project is licensed under the MIT License - see the LICENSE file for details.
