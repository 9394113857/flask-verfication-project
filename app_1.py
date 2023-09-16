import sys
from calendar import timegm
from datetime import datetime, timedelta

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
from authy.api import AuthyApiClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'raghu'
app.config['MYSQL_DB'] = 'crud_flask'

# Initialize the JWTManager
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

mysql = MySQL(app)

# Authy Configuration
api = AuthyApiClient('UWhD3LN4SmblV4vhaVl2g1qaKBi82cph')


@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    # Your code for handling GET and POST requests here
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE (username = %s )", (username,))
        details = cursor.fetchone()
        if details is None:
            return ({"message": "No details"}), 401
        hashed_password = details["password"]
        password_match = check_password_hash(hashed_password, password)

        if password_match:
            session['loggedin'] = True
            session['id'] = details['id']
            session['username'] = details['username']

            if not details.get('phone_verified'):
                return redirect(url_for('phone_verification'))

            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', title="Login")


@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form \
            and 'firstname' in request.form and 'lastname' in request.form and 'phonenumber' in request.form:
        username = request.form['username']
        password = request.form['password']
        hassedpassword = generate_password_hash(password)
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phonenumber = request.form['phonenumber']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not firstname or not lastname or not phonenumber:
            msg = 'Please fill out the form!'
        else:
            cursor.execute(
                'INSERT INTO accounts(username, password, email, firstname, lastname, phonenumber, phone_verified) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (username, hassedpassword, email, firstname, lastname, phonenumber, False))
            mysql.connection.commit()

            session['registered'] = True
            session['username'] = username
            session['phone_number'] = phonenumber

            api.phones.verification_start(phonenumber, country_code='US', via='sms')

            return redirect(url_for('phone_verification'))
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


@app.route('/pythonlogin/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/pythonlogin/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/pythonlogin/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))


@app.route("/phone_verification", methods=["GET", "POST"])
def phone_verification():
    if request.method == "POST":
        country_code = request.form.get("country_code")
        phone_number = request.form.get("phone_number")
        method = request.form.get("method")

        session['country_code'] = country_code
        session['phone_number'] = phone_number

        api.phones.verification_start(phone_number, country_code, via=method)

        return redirect(url_for("verify"))

    return render_template("phone_verification.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        token = request.form.get("token")

        phone_number = session.get("phone_number")
        country_code = session.get("country_code")

        verification = api.phones.verification_check(phone_number, country_code, token)

        if verification.ok():
            # Update phone_verified in the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("UPDATE accounts SET phone_verified = %s WHERE phonenumber = %s", (True, phone_number))
            mysql.connection.commit()

            # Phone verified successfully, redirect to login page
            return redirect(url_for('login'))
        else:
            # Verification failed, render verify.html with error message
            error_message = "Invalid verification code. Please try again."
            return render_template("verify.html", error_message=error_message)

    return render_template("verify.html")

##########

@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        if 'username' in request.form and 'phonenumber' in request.form:
            username = request.form['username']
            phonenumber = request.form['phonenumber']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM accounts WHERE (username = %s AND phonenumber = %s)", (username, phonenumber))
            details = cursor.fetchone()
            if details is None:
                return ({"message": "Invalid username or phone number"}), 401
            else:
                api.phones.verification_start(phonenumber, country_code='91', via='call')  # Hardcoded values
                session['username'] = username
                session['phone_number'] = phonenumber
                return redirect(url_for('password_reset_verification'))
        else:
            return ({"message": "Invalid request"}), 400

    # Display the form for GET requests
    return render_template('password_reset.html')

@app.route("/password_reset_verification", methods=["GET", "POST"])
def password_reset_verification():
    if request.method == "POST":
        phone_number = session.get("phone_number")
        country_code = 91
        token = request.form.get("token")

        # Check verification
        verification = api.phones.verification_check(phone_number,
                                                     country_code,
                                                     token)

        if verification.ok():
            return redirect(url_for('display_reset_password'))
        else:
            error_message = "Invalid verification code. Please try again."
            return render_template("password_reset_verification.html", error_message=error_message)

    return render_template("password_reset_verification.html")

@app.route('/display_reset_password')
def display_reset_password():
    return render_template('reset_password.html')


@app.route('/reset_password', methods=['POST'])
def reset_password():
    if 'new_password' in request.form:
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password)

        username = session['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE accounts SET password = %s WHERE username = %s", (hashed_password, username))
        mysql.connection.commit()

        return redirect(url_for('login'))
    else:
        return ({"message": "Invalid request"}), 400



###############


if __name__ == "__main__":
    app.run(debug=True)

    # # Check if a custom port was provided as a command-line argument
    # if len(sys.argv) > 1:
    #     custom_port = sys.argv[1]
    # else:
    #     custom_port = input("Enter port number (Press Enter for default 5000): ").strip()
    #
    # port = int(custom_port) if custom_port else 5000

    # app.run(debug=True, port=port)
