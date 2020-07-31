import json
from flask import Flask, jsonify, render_template, flash, request, redirect, url_for, session, jsonify
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, save_json, db2, save_json2
import matplotlib.pyplot as plt

import pandas as pd
import xlrd

import requests

app = Flask(__name__)
mysql = MySQL(app)
app.secret_key = 'your secret key'

# Database connection details below
#  USed the mysql dbms to handle the user authentication system

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'flask_system'
mysql.init_app(app)


@app.route('/')
def home_page():
    save_generated_figure()
    return render_template('home.html')


@app.route('/loginpage')
def login_page():
    return render_template('login.html')


# Only accepts the method POST

@app.route('/login', methods=['POST'])
def login(cursor=None, conn=None):
    # Accepting the data from the filled form

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
                return render_template('login.html', error="Password error")
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

            cursor.execute('SELECT * FROM clients WHERE username = %s ', (_name,))
            if cursor.fetchall().__len__() == 0:
                cursor.execute(sql_q, data)
                conn.commit()
                flash("Successful login")
                return render_template('login.html')
            else:
                flash("User name already exists in the table")
                return render_template('base.html')
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


@app.route('/dashboard/addclient', methods=['post'])
def addclients():
    if request.method == "POST":
        newClient = {
            'Client_Name': request.form['uname'],
            'Client_Address': request.form['uaddress'],
            'Client_Phone': request.form['uphone'],
            'Client_Due': request.form['udue'],
            'Client_Paid': request.form['upaid']
        }

        db.append(newClient)
        save_json()
        return redirect(url_for('home_page'))
    else:
        return "error loading the file"


#  method to add the item in json
@app.route('/dashboard/addItem/', methods=['post'])
def addItem():
    if request.method == "POST":
        newItem = {
            'Index': len(db2) + 1,
            'Name': request.form['iname'],
            'Rate': request.form['sprice'],
            'Count': request.form['ucount'],
        }

        db2.append(newItem)
        save_json2()
        return redirect(url_for('showdashboard', itemcount=(len(db2) + 5) / 5))
    else:
        return "error loading the file"


@app.route('/dashboard/about')
def aboutpage():
    return render_template('about.html')


@app.route('/dashboard')
def showd():
    return redirect(url_for('showdashboard', itemcount=1))


@app.route('/dashboard/<int:itemcount>')
def showdashboard(itemcount):
    try:
        sum = 0
        paid = 0
        for i in range(0, len(db)):
            paid += int(db[i]['Client_Paid'])
            sum += int(db[i]['Client_Due'])
        begin = (itemcount - 1) * 5
        _paginator_list = list(range(1, int(len(db2) / 5) + 2, 1))
        print(save_generated_figure())

        return render_template('dashboard.html', length=len(db), due=sum, paid=paid, items=db2[begin:begin + 5],
                               itemcount=itemcount, list=_paginator_list)
    except Exception as e:
        return str(e)


def save_generated_figure():
    try:
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('equal')
        labels=[]
        sizes=[]
        for i in db:
                labels.append(i['Client_Name'])
                sizes.append(i['Client_Due'])

        colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.savefig('static/images/Generated/pie.png')
        return
    except Exception as e:
        return e


@app.route('/api/items')
def api_all_card_route():
    return jsonify(db2)


@app.route('/dashboard/generate_bill')
def a_tag():
    # methods to calculate about the corona virus details

    return render_template('Bill.html', users=db)


@app.route('/dashboard/get_details', methods=['post'])
def a_tag2():
    # methods to calculate about the corona virus details
    for i in db:
        if i['Client_Name'] == request.form['user']:
            value = i
    return render_template('Bill.html', users=db, value=value)


@app.route('/dashboard/update', methods=['post'])
def update():
    # updating the data
    for i in db:
        if i['Client_Name'] == request.form['uname'] and int(i['Client_Due']) >= int(request.form['paying_amt']):
            i['Client_Due'] = str(int(i['Client_Due']) - int(request.form['paying_amt']))
            value = i
            Rem = i['Client_Due']
            save_json()

            create_bill(name=i['Client_Name'], paid=request.form['paying_amt'], rem=i['Client_Due'])
            nor = False
            break

        else:
            nor = True

    date = request.form['Date']

    if (nor):
        return "Supply valid message"
    return render_template('Bill.html', users=db, value=value, value1=value, date=date, Rem=Rem,
                           paid=request.form['paying_amt'])


# method that handles the bill generation in csv format

def create_bill(name, paid, rem):
    bill_template = pd.DataFrame({'S.No.': 1, 'User Name': [name],
                                  'Paid Amount': [paid],
                                  'Remaining Balance': [rem]})

    try:
        bill_template.to_excel('static/Bill/gene.xlsx')
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    app.run()
