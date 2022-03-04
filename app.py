from flask import Flask, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL, MySQLdb
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
import random, string

app = Flask(__name__)
app.config['SECRET_KEY'] = "thisisasecret"
Bootstrap(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'm10j28r00'
app.config['MYSQL_DB'] = 'user_system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=50)])

class ChangePasswordForm(FlaskForm):
    oldPassword = PasswordField('Old Password', validators=[InputRequired(), Length(min=8, max=50)])
    newPassword = PasswordField('New Password', validators=[InputRequired(), Length(min=8, max=50)])

@app.route('/')
def index():
    form = LoginForm()
    return render_template('loginpage.html', form = form)

@app.route('/profilepage')
def profilepage():
    return render_template('profilepage.html', username = session['users_username'])

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        message = "Invalid username and password"
        username = form.username.data
        password = form.password.data
        key = "secretkey"

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(''' SELECT users_emp_idnum, users_username FROM users WHERE users_username = %s AND AES_DECRYPT(users_password, %s) = %s''', (username, key, password))
        user = cursor.fetchall()

        if len(user) == 1:
            session['loggedin'] = True
            session['users_emp_idnum'] = user[0]['users_emp_idnum']
            session['users_username'] = user[0]['users_username']
            return redirect(url_for('profilepage', form = form, username = session['users_username']))

        else:
            return render_template('loginpage.html', form = form, message = message)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('users_emp_idnum', None)
    session.pop('users_username', None)
    return redirect(url_for("index"))

@app.route('/changepasspage')
def changepasspage():
    form = ChangePasswordForm()
    return render_template('changepass.html', form = form)

@app.route('/changepassword', methods = ['GET', 'POST'])
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        username = session['users_username']
        oldPassword = form.oldPassword.data
        newPassword = form.newPassword.data
        key = "secretkey"

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(''' UPDATE users SET users_password = AES_ENCRYPT(%s, %s) WHERE users_username = %s AND AES_DECRYPT(users_password, %s) = %s ''', (newPassword, key, username, key, oldPassword))
        mysql.connection.commit()
        cursor.close()
        return render_template('profilepage.html', form = form, username = session['users_username'])

@app.route('/resetpassword', methods = ['GET', 'POST'])
def resetpassword():
    letters = string.ascii_letters
    digits = string.digits
    username = session['users_username']
    key = "secretkey"
    newPassword = "".join(random.choice(letters + digits) for i in range(10))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(''' UPDATE users SET users_password = AES_ENCRYPT(%s, %s) WHERE users_username = %s''', (newPassword, key, username))
    mysql.connection.commit()
    cursor.close()
    return render_template("profilepage.html", username = session['users_username'], password = newPassword)


if __name__ == "__main__":
    app.run(debug = True)