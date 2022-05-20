import smtplib
from flask import Flask, redirect, render_template, session, url_for, request
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL, MySQLdb
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
import random, string

app = Flask(__name__)
app.config['SECRET_KEY'] = "thisisasecret"
otp = ''
hasRequestedOTP = False
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

class OTPForm(FlaskForm):
    otp = StringField('OTP', validators=[InputRequired(), Length(min=6, max=6)])

@app.route('/')
def index():
    global otp
    global hasRequestedOTP
    form = LoginForm()
    return render_template('loginpage.html', form = form)

@app.route('/profilepage', methods = ['POST'])
def profilepage():
    global otp
    global hasRequestedOTP
    return render_template('profilepage.html', username = session['users_username'])

@app.route('/otppage')
def otppage():
    global otp
    global hasRequestedOTP
    form = OTPForm()
    return render_template('otppage.html', form = form, username = session['users_username'])

@app.route('/login', methods = ['GET', 'POST'])
def login():
    global otp
    global hasRequestedOTP
    form = LoginForm()
    if form.validate_on_submit():
        message = "Invalid username and password"
        username = form.username.data
        password = form.password.data
        key = "secretkey"

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(''' SELECT users_emp_idnum, users_username FROM users WHERE users_username = %s 
        AND AES_DECRYPT(users_password, %s) = %s''', (username, key, password))
        user = cursor.fetchall()

        if len(user) == 1:
            session['loggedin'] = True
            session['users_emp_idnum'] = user[0]['users_emp_idnum']
            session['users_username'] = user[0]['users_username']
            return redirect(url_for('otp_request', form = form, username = session['users_username']))

        else:
            return render_template('loginpage.html', form = form, message = message)

def otp_generator():
    number_string = ''
    for i in range (0,6):
        number_string += str(random.randint(0,9))
    return number_string

@app.route('/otp_request', methods=['POST', 'GET'])
def otp_request():
    global otp
    global hasRequestedOTP
    form = OTPForm()

    if hasRequestedOTP == False:
        otp = otp_generator()
        hasRequestedOTP = True

        email_request = smtplib.SMTP("smtp.gmail.com", port = 587)
        email_request.starttls()
        email_request.login("michaeljoy.rodriguez@g.msuiit.edu.ph", "xxspkphyvawrsbdp")
        email = "michaeljoy.rodriguez@g.msuiit.edu.ph"
        email_request.sendmail('&&&&&&&&&&&',email, str(otp))

    if request.method == 'POST':
        if otp == request.form['otp']:
            return redirect(url_for('profilepage'))
        else:
            return "<p>" + "Incorrect OTP was entered" + "</p>"
    else:
        return render_template('otppage.html', context = {"status": otp}, form = form)
        

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    global otp
    global hasRequestedOTP
    session.pop('loggedin', None)
    session.pop('users_emp_idnum', None)
    session.pop('users_username', None)
    hasRequestedOTP = False
    otp = ''
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug = True)