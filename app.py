import json

from flask import Flask, render_template, flash, request, redirect, url_for, session
from flaskext.mysql import MySQL
from pip._vendor.requests import Session
from werkzeug.security import generate_password_hash, check_password_hash

# from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'flask_system'
mysql.init_app(app)


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/loginpage')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login(cursor=None, conn=None):
    _username = request.form['uemail']
    _password = request.form['upassword']

    if 'username' not in session:
        if request.method == 'POST' and _password and _username:

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients WHERE username = %s ', (_username,))
            # Fetch one record and return result
            account = cursor.fetchall()
            milyo = account[0][1]

            if (check_password_hash(milyo, _password)):
                session['user'] = account[0][0]
                return render_template('home.html')
        else:
            error = "fill the correct credentials"
    else:
        return render_template('login.html')

    return render_template('login.html', error=error)


@app.route('/signup', methods=['POST'])
def signup():
    cursor = None
    conn = None
    try:
        _name = request.form['uemail']
        _phone = request.form['uphone']
        _password = request.form['upassword']
        _address = request.form['uaddress']

        if _name and _phone and _password and _address and request.method == 'POST':
            _hashed_password = generate_password_hash(_password, "sha256")
            sql_q = "INSERT INTO clients(username,password,phone,address) VALUES(%s, %s, %s, %s)"
            data = (_name, _hashed_password, _phone, _address,)

            conn = mysql.connect()
            # connection is created now
            cursor = conn.cursor()
            # cursor is used for sql commands
            cursor.execute(sql_q, data)
            conn.commit()
            flash("Successful login")
            return render_template('login.html')
        else:
            flash("User provided wrong credentials")
            return ('Error loading the data')
    except Exception as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


@app.route('/register')
def register_page():
    return render_template('base.html')


@app.route('/user/')
def show_userDetails():
    return "user details"


@app.route('/signout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
if __name__ == '__main__':
    app.run()
