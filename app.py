# Importing all important modules
from flask import Flask, flash, logging, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
from functools import wraps
from passlib.hash import bcrypt_sha256
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email, Length, EqualTo)

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

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.secret_key = '$2a$12$xRQceJ9HJgc0gPOFub84EuM2bH1OKiYCisnVg1OZLwTZG/AZAMd9a'
    app.run(debug=True)    