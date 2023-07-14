from flask import Flask, render_template, request

app = Flask(__name__)
app.debug = True

@app.route('/report', methods=['POST'])
def report():
    username = request.form.get('username')
    password = request.form.get('password')

    # Perform password validation
    valid = (
        len(password) >= 8
        and any(char.islower() for char in password)
        and any(char.isupper() for char in password)
        and password[-1].isdigit()
    )

    return render_template('report.html', username=username, password=password, valid=valid)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/navbar')
def navbar():
    return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True)
