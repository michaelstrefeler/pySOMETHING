# Importing all important modules
from flask import Flask, flash, logging, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
from functools import wraps
from passlib.hash import bcrypt_sha256
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email, Length, EqualTo)
import time

app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pysomething'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Init MySQL
mysql = MySQL(app)

# Index
@app.route('/')
def index():
    return render_template('home.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Resister form class
class RegisterForm(Form):
    name = StringField('Full Name', validators = [Length(min = 8, max = 150)])
    email = StringField('Email', validators = [Length(min = 15, max = 225)])
    password = PasswordField('Password', validators = [DataRequired(), EqualTo('confirm', message = 'Passords do not match')])
    confirm = PasswordField('Confirm Password')

# Register
@app.route('/register', methods = ['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = bcrypt_sha256.hash(str(form.password.data))

        # Create cursor
        cursor = mysql.connection.cursor()

        # Execute query
        cursor.execute("INSERT INTO t_user(use_name, use_email, password) VALUES(%s, %s, %s)", (name, email, password))

        # Commit to database
        mysql.connection.commit()

        # Close cursor
        cursor.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        cursor = mysql.connection.cursor()

        result = cursor.execute("SELECT * FROM t_user WHERE use_email = %s", [email])

        if result > 0:
            data = cursor.fetchone()
            password = data['password']
            if bcrypt_sha256.verify(password_candidate, password):
                session['logged_in'] = True
                session['user'] = data['use_name']
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid credentials'
            return render_template('login.html', error = error)
        else:
            error = 'No user found'
            return render_template('login.html', error = error)
        cursor.close()
    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cursor = mysql.connection.cursor()

    result = cursor.execute("SELECT * FROM t_list WHERE lis_author = %s", [session['user']])

    lists = cursor.fetchall()

    if result > 0:
        return render_template('dashboard.html', lists = lists)
    else:
        error = "You don't have any lists"
        return render_template('dashboard.html', error = error)
    cursor.close()

# Lists
@app.route('/lists')
@is_logged_in
def lists():
    cursor = mysql.connection.cursor()

    result = cursor.execute("SELECT * FROM t_list WHERE lis_author = %s", [session['user']])

    lists = cursor.fetchall()

    if result > 0:
        return render_template('lists.html', lists = lists)
    else:
        error = 'No lists found'
        return render_template('lists.html', error = error)

    cursor.close()

# Single list
@app.route('/list/<int:id>')
@is_logged_in
def list(id):
    cursor = mysql.connection.cursor()

    result = cursor.execute("SELECT idList,`lis_title`,lis_author, t_item.ite_description FROM `t_list` NATURAL JOIN t_item WHERE t_item.for_list = idList AND idList = %s AND lis_author = %s ",([id], [session['user']]))

    list = cursor.fetchall()

    if result > 0:
        return render_template('list.html', list = list, result = result)
    elif result == 0:
        error = 'None of your lists have that id'
        return render_template('list.html', error = error)

    cursor.close()

# List form class
class ListForm(Form):
    title = StringField('List title', validators = [Length(min = 4, max = 100)])
    items = TextAreaField('List items', validators = [Length(min = 4)])

# Add list
@app.route('/add_list', methods = ['GET', 'POST'])
@is_logged_in
def addList():
    form = ListForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        items = form.items.data
        arr_item = items.splitlines()

        # Create cursor
        cursor = mysql.connection.cursor()

        ###### Adding list ######
        # Executing query
        cursor.execute("INSERT INTO t_list(lis_title, lis_author) VALUES(%s, %s)", (title, [session['user']]))

        # Commit to database
        mysql.connection.commit()
        # Close cursor
        cursor.close()

        # Getting the ID of the list that was just added
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT idList FROM t_list ORDER BY idList DESC LIMIT 1")
        list_id = cursor.fetchone()
        cursor.close()
        ###### Adding the items ######
        # Create cursor
        cursor = mysql.connection.cursor()
        for item in arr_item:
            cursor.execute(
                "INSERT INTO t_item(ite_description, for_list) VALUES(%s, %s)",([item], [list_id['idList']]))
            mysql.connection.commit()
        # Close cursor
        cursor.close()

        flash('Your list has been added', 'success')

        return redirect(url_for('lists'))
    return render_template('addList.html', form = form)

# Edit list
@app.route('/edit_list/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_list(id):
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT idList,lis_title,lis_author, t_item.ite_description FROM t_list NATURAL JOIN t_item WHERE t_item.for_list = idList AND idList = %s AND lis_author = %s ",([id], [session['user']]))

    list = cursor.fetchall()

    form = ListForm(request.form)

    # Populate form fields
    form.title.data = list[0]['lis_title']

    list_items = []
    for i in range(0, len(list)):
        list_items.append(list[i]['ite_description'])

    list_items = str(list_items)
    list_items = list_items.replace('[', '')
    list_items = list_items.replace(']', '')
    list_items = list_items.replace(',', '\n')
    list_items = list_items.replace('\'', '')
    form.items.data = list_items
    return render_template('edit_list.html', form=form)

# Delete list
@app.route('/delete_list/<int:id>', methods=['POST'])
@is_logged_in
def delete_list(id):
    # Create cursor
    csr = mysql.connection.cursor()
    
    # Delete article
    csr.execute("DELETE FROM t_list WHERE idList = %s",[id])
    
    # Commit to DB
    mysql.connection.commit()
    
    # Close cursor
    csr.close()

    csr = mysql.connection.cursor()

    csr.execute("DELETE FROM t_item WHERE for_list = %s", [id])
    mysql.connection.commit()
    csr.close()

    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key = '$2a$12$xRQceJ9HJgc0gPOFub84EuM2bH1OKiYCisnVg1OZLwTZG/AZAMd9a'
    app.run(debug=True)
