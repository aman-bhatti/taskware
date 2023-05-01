from flask import Flask, render_template, request, redirect, url_for, session, jsonify, request, flash
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

@app.route('/calender')
def calender():
    return render_template('calender.html')

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
        if 'loggedin' in session:
            return redirect('dashboard.html')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM users WHERE username = %s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute(
                'INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Check if user is logged in
    if 'loggedin' in session:
        # Retrieve user data from database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        user = cursor.fetchone()
        
         # Delete old user record
        # cursor.execute('DELETE FROM users WHERE username=%s AND id=%s',(user['username'], session['id']))
        # mysql.connection.commit()
    
        if request.method == 'POST':
            # Get form data
            new_username = request.form['username']
            new_password = request.form['password']
            new_email = request.form['email']

            
            # Insert new user record with updated information
            cursor.execute(
                'INSERT INTO users (id, username, password, email) VALUES (%s, %s, %s, %s)',
                (session['id'], new_username, new_password, new_email))
            mysql.connection.commit()
            flash('Profile updated successfully!', 'success')

            # Update user data in session
            user['username'] = new_username

            # Retrieve updated user data from database
            cursor.execute('SELECT * FROM users WHERE id = %s',
                           (session['id'],))
            user = cursor.fetchone()

           
        # Render profile page with pre-populated form fields
        return render_template('profile.html', user=user)

    # If user is not logged in, redirect to login page
    else:
        return redirect('/login')

    
@app.route('/deleteUser', methods=['POST'])
def deleteUser():
    if 'loggedin' in session:
        # Retrieve user data from database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        user = cursor.fetchone()
        
        #  # Delete old user record
        # cursor.execute('DELETE FROM users WHERE username=%s AND id=%s',(user['username'], session['id']))
        # mysql.connection.commit()
    
        if request.method == 'POST':
            # Get form data
            new_username = request.form['username']
            new_password = request.form['password']
            new_email = request.form['email']

            
            # Insert new user record with updated information
            # cursor.execute(
            #     'INSERT INTO users (id, username, password, email) VALUES (%s, %s, %s, %s)',
            #     (session['id'], new_username, new_password, new_email))
            # mysql.connection.commit()
            # flash('Profile updated successfully!', 'success')
            cursor.execute(
            'UPDATE users SET username = %s, password = %s, email = %s WHERE id = %s',
            (new_username, new_password, new_email, session['id']))
            mysql.connection.commit()
            flash('Profile updated successfully!', 'success')


            # Update user data in session
            user['username'] = new_username

            # Retrieve updated user data from database
            cursor.execute('SELECT * FROM users WHERE id = %s',
                           (session['id'],))
            user = cursor.fetchone()

            session.pop('loggedin', None)
        # Render profile page with pre-populated form fields
        return redirect('/logout')
        # return render_template('profile.html', user=user)

    # If user is not logged in, redirect to login page
    else:
        return redirect('/login')


    # <form method="post" action="{{ url_for('register') }}">
def get_user_data():
    if 'loggedin' in session:
        # Retrieve user data from database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        user = cursor.fetchone()
        cursor.close()

        # If user data is found, return the user dictionary
        if user:
            return user

    # If user data is not found, return None
    return None

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
    user = get_user_data()

    # If user is not logged in, redirect to login page
    if not user:
        return redirect('/login')

    # Render dashboard template with user data
    return render_template('calendar.html', user=user)


@app.route('/notes')
def notes():
    user = get_user_data()

    # If user is not logged in, redirect to login page
    if not user:
        return redirect('/login')

    # Render dashboard template with user data
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM notes WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
        notes = cursor.fetchall()
        if notes:
            print(notes)
    return render_template('notes.html', user=user , notes=notes)

@app.route('/contacts')
def contacts():
    user = get_user_data()

    # If user is not logged in, redirect to login page
    if not user:
        return redirect('/login')

    # Render dashboard template with user data
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM contacts WHERE user_id = %s ORDER BY name asc', (user_id,))
        #cursor.execute('SELECT * from contacts order by name asc')
        contacts = cursor.fetchall()
        if contacts:
            print(contacts)
        return render_template('contacts.html', user=user , contacts=contacts)



@app.route('/toDo')
def toDo():
    user = get_user_data()
    # If user is not logged in, redirect to login page
    if not user:
        return redirect('/login')
    # Render dashboard template with user data
    return render_template('toDo.html', user=user)


@app.route('/pomodoro')
def pomodoro():
    user = get_user_data()
    # If user is not logged in, redirect to login page
    if not user:
        return redirect('/login')
    # Render dashboard template with user data
    return render_template('pomodoro.html', user=user)

@app.route('/save-note', methods=['POST'])
def saveNote():
    requestData = request.get_json()
    priority = requestData.get('priority')
    text = requestData.get('text')
    user_id = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "INSERT INTO notes(text, priority, user_id) VALUES (%s,%s,%s)", (text, priority, user_id))
    mysql.connection.commit()
    return redirect(url_for('notes'))

@app.route('/save-contact', methods=['POST'])
def saveContact():
    requestData = request.get_json()
    contact = requestData.get('contact')
    name = requestData.get('name')
    user_id = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "insert into contacts(name, contact, user_id) VALUES (%s,%s,%s)", (name, contact, user_id))
    mysql.connection.commit()
    return redirect(url_for('contacts'))


# Here is the route for the delete note from the database

@app.route('/delete-note/<int:note_id>', methods=['DELETE'])
def deleteNote(note_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    mysql.connection.commit()
    return redirect(url_for('contacts'))

# Here is the route for the edit note from the database using PUT operation

@app.route('/update-note/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    requestData = request.get_json()
    text = requestData.get('text')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "UPDATE notes SET text = %s WHERE id = %s", (text, note_id))
    mysql.connection.commit()
    return redirect(url_for('notes'))

@app.route('/search-contact', methods=['POST'])
def searchContact():
    search_name = request.form['search_name']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM contacts WHERE name LIKE %s", ("%" + search_name + "%",))
    contacts = cursor.fetchall()
    return render_template('contacts.html', contacts=contacts)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    # session.pop('id', None)
    # session.pop('username', None)
    return redirect(url_for('login'))

    
@app.route('/search')
def search():
    # Get the search term from the query string
    query = request.args.get('q')

    # If no search term is entered, render the search page with no results
    if not query:
        return render_template('search_results.html', query=None)

    # Define a dictionary of page routes that can be searched
    routes = {
        'home': '/',
        'profile': '/profile',
        'dashboard': '/dashboard',
        'contact': '/contact',
        'about': '/about',
        'notes': '/notes',
        'calendar': '/calendar',
        'services': '/services',
        'connect': '/connect',
        'pomodoro': '/pomodoro',
        'pomodoro timer': '/pomodoro',
        'tasks': '/toDo',
        # Add more page routes as needed
    }

    # Check if the search term matches a page route and redirect to it if found
    if query in routes:
        return redirect(routes[query])

    # If the search term does not match a page route, render a search results page
    return render_template('search_results.html', query=query)

if __name__ == '__main__':
    app.debug = True
    app.run()
