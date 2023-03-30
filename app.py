from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from jinja2 import Template

   

app = Flask(__name__, template_folder='templates')


app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'us-cdbr-east-06.cleardb.net'
app.config['MYSQL_USER'] = 'b1c81d9b028a9f'
app.config['MYSQL_PASSWORD'] = 'a4323524'
app.config['MYSQL_DB'] = 'heroku_b673ba97fe8636f'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('main.html')


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('dashboard.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('dashboard.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute(
                'INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/connect')
def connect():
    return render_template('connect.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/calendar')
def calendar():
    return render_template('calendar.html')


@app.route('/notes')
def notes():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from notes order by created_at desc')
    notes = cursor.fetchall()
    if notes:
        print(notes)
    return render_template('notes.html', notes=notes)

@app.route('/contacts')
def contacts():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from contacts order by name asc')
    contacts = cursor.fetchall()
    if contacts:
        print(contacts)
    return render_template('contacts.html', contacts=contacts)


# @app.route('/contacts')
# def contacts():
#     return render_template('contacts.html')


@app.route('/toDo')
def toDo():
    return render_template('toDo.html')


@app.route('/pomodoro')
def pomodoro():
    return render_template('pomodoro.html')


@app.route('/save-note', methods=['POST'])
def saveNote():
    requestData = request.get_json()
    priority = requestData.get('priority')
    text = requestData.get('text')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "INSERT INTO notes (text, priority) value (%s,%s)", (text, priority))
    mysql.connection.commit()
    return redirect(url_for('notes'))

@app.route('/save-contact', methods=['POST'])
def saveContact():
    requestData = request.get_json()
    contact = requestData.get('contact')
    name = requestData.get('name')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "insert into contacts(name, contact) value (%s,%s)", (name, contact))
    mysql.connection.commit()
    return redirect(url_for('contacts'))


if __name__ == '__main__':
    app.debug = True
    app.run()