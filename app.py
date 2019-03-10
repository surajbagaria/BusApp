from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask_recaptcha import ReCaptcha
from passlib.hash import sha256_crypt
from flask_googlemaps import GoogleMaps
import os
import urllib.request
import ssl
import simplejson as json
import requests

app = Flask(__name__)

#config MySQL

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Suraj@123'
app.config['MYSQL_DB'] = 'myapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

#config GoogleMaps
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBf2CZVNafcGGeYFzG7w5JBOcFY6cHN6-4"

#init GoogleMaps
googlemaps = GoogleMaps(app)

#config Recaptcha
siteKey = '6Ldnm5YUAAAAAJCB5ktHWwiE9NkLkl9uK71bJCMa'
secretKey = '6Ldnm5YUAAAAANAOGEtd441_niZf8-nvAtvmt-l4'
app.config.update({'RECAPTCHA_ENABLED': True,
                   'RECAPTCHA_SITE_KEY':
                       siteKey,
                   'RECAPTCHA_SECRET_KEY':
                       secretKey})


#init Recaptcha
recaptcha = ReCaptcha(app=app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
Articles = Articles()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html',articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html',id=id)

class RegisterationForm(Form):
    name= StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Pasword do not match')])
    confirm = PasswordField('Confirm Password')

class DirectionForm(Form):
    origin = StringField('Origin', [validators.Length(min=1, max=50)])
    destination = StringField('Destination', [validators.Length(min=1, max=50)])

#dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    API_KEY = 'AIzaSyBf2CZVNafcGGeYFzG7w5JBOcFY6cHN6-4'
    print(API_KEY)
    form = DirectionForm(request.form)
    if request.method == 'POST' and form.validate():
        print('Inside')
        origin = form.origin.data
        ori = origin.replace(' ', '+')
        destination = form.destination.data
        dest = destination.replace(' ', '+')
        nav_request = 'origin={}&destination={}&key={}'.format(ori, dest, API_KEY)
        gcontext = ssl.SSLContext()
        req = endpoint + nav_request
        print(req)
        response = urllib.request.urlopen(req, context=gcontext).read()
        directions = json.loads(response)
        end_loc=directions['routes'][0]['legs'][0]['end_location']
        start_loc=directions['routes'][0]['legs'][0]['start_location']

        print("the end loc is: ",end_loc)
        print("the start loc is: ",start_loc)
        session['origin'] = origin
        session['destination']= destination
        end_lat= end_loc['lat']
        print(end_lat)
        end_lng= end_loc['lng']
        print(end_lng)
        start_lat= start_loc['lat']
        print(start_lat)
        start_lng= start_loc['lng']
        print(start_lng)
        session['end_lat'] = end_lat
        session['end_lng']= end_lng
        session['start_lat'] = start_lat
        session['start_lng']= start_lng
        #return render_template('dashboard.html', form=form)
        return redirect(url_for('what'))
    return render_template('dashboard.html',form=form)



#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterationForm(request.form)
    print('Hi')
    if request.method == 'POST' and form.validate():
        print('Ok')
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.hash(str(form.password.data))
        r = requests.post('https://www.google.com/recaptcha/api/siteverify',data = {'secret' : secretKey,'response' :request.form['g-recaptcha-response']})
        google_response = json.loads(r.text)
        print('JSON: ', google_response)
        if google_response['success']:
            print('SUCCESS')
            #create Cursor
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))
            #commit to DB
            mysql.connection.commit()
            #close the connection
            cur.close()
            flash('you are now registered and can login', 'Success')
            return redirect(url_for('login'))
        else:
            error = 'you may be a robot'
            return render_template('register.html', error=error, form=form)
    return render_template('register.html', form=form)

#User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #create Cursor
        cur = mysql.connection.cursor()

        #get user by Username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            #compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                #Passed
                session['logged_in'] = True
                session['username'] = username
                flash('you are now logged in', 'success')
                return redirect(url_for('dashboard'))


            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')


#logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))

#google test
@app.route('/googletest')
def googletest():
    return render_template('googletest.html')

#what test
@app.route('/what')
def what():
    return render_template('what.html')


if __name__ == '__main__':
    app.run(debug=True)
