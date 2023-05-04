from flask import Flask, render_template, request, redirect, url_for, session, jsonify, request, flash
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re
from jinja2 import Template
import mysql.connector
from datetime import datetime, timedelta


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
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        cursor.execute('SELECT * FROM todos WHERE user_id = %s ORDER BY due_date', (user_id,))
        todos = cursor.fetchall()

        if request.method == 'POST':
            # Get list of task IDs to delete
            task_ids = request.form.getlist('task_checkbox')
            if task_ids:
                # Delete selected tasks
                task_id_str = ','.join([str(id) for id in task_ids])
                sql = f"DELETE FROM todos WHERE id IN ({task_id_str})"
                cursor.execute(sql)
                mysql.connection.commit()

                # flash('Selected tasks deleted successfully!', 'success')

            return redirect(url_for('dashboard'))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT login_count FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        if account:
            login_count = account['login_count']
        return render_template('dashboard.html', user=user, todos=todos , login_count = login_count)

    else:
        return redirect(url_for('login'))



@app.route('/calendar')
def calendar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, task, due_date FROM todos WHERE user_id = %s", (session['id'],))
    tasks = {}
    for task in cur.fetchall():
        if task[2] is not None:
            date_str = task[2].strftime('%Y-%m-%d')
            if date_str not in tasks:
                tasks[date_str] = []
            tasks[date_str].append({'id': task[0], 'title': task[1]})

    cur.close()
    print(tasks)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
            'SELECT login_count FROM users WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    if account:
        login_count = account['login_count']
    return render_template('calendar.html', tasks=tasks , login_count = login_count)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if 'loggedin' in session:
        return redirect(url_for('dashboard'))

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
            if 'login_count' not in session:
                session['login_count'] = 1
                cursor.execute(
                    'UPDATE users SET login_count = login_count + 1 WHERE id = %s', (session['id'],))
                mysql.connection.commit()
            msg = 'Logged in successfully !'
            return redirect(url_for('dashboard', msg=msg))
        if 'loggedin' in session:
            return redirect(url_for('dashboard'))
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
        
        # Set default login count to 0
            login_count = 0

        # Insert user data into database
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO users (username, password, email, login_count) VALUES (%s, %s, %s, %s)', (username, password, email, login_count))
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
        return redirect('/login')
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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT login_count FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        if account:
            login_count = account['login_count']    
    return render_template('notes.html', user=user , notes=notes , login_count = login_count)

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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT login_count FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        if account:
            login_count = account['login_count']
        return render_template('contacts.html', user=user , contacts=contacts , login_count = login_count)


@app.route('/toDo')
def toDo():
    if 'loggedin' in session:
        user_id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM todos WHERE user_id = %s', (user_id,))
        todos = cur.fetchall()
        cur.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT login_count FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        if account:
            login_count = account['login_count']
        return render_template('toDo.html', todos=todos , login_count = login_count)

@app.route('/add-todo', methods=['POST'])
def add_todo():
    todo = request.form['task']
    start_date = request.form['due_date']
    user_id = session['id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("INSERT INTO todos (user_id, task, due_date) VALUES (%s, %s, %s)", (user_id, todo, start_date))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('toDo'))

@app.route('/add-calendar-todo', methods=['POST'])
def add_calendar_todo():
    todo = request.form['task']
    start_date = request.form['due_date']
    user_id = session['id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("INSERT INTO todos (user_id, task, due_date) VALUES (%s, %s, %s)", (user_id, todo, start_date))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('calendar'))



@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('toDo'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_todo(id):
    data = request.get_json()
    new_task = data['task']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE todos SET task = %s WHERE id = %s', (new_task, id))
    mysql.connection.commit()
    cursor.close()
    mysql.connection.close()
    return '', 204


@app.route('/pomodoro')
def pomodoro():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT login_count FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        if account:
            login_count = account['login_count']
            return render_template('pomodoro.html', login_count=login_count)
        else:
            return redirect('/')
    return redirect('/login')

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

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('main'))


    
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
        'contacts': '/contact',
        'about': '/about',
        'notes': '/notes',
        'calendar': '/calendar',
        'services': '/services',
        'connect': '/connect',
        'pomodoro': '/pomodoro',
        'pomodoro timer': '/pomodoro',
        'tasks': '/toDo',
        'setting': '/profile',
        'Setting': '/profile',
        'logout': '/login',
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
