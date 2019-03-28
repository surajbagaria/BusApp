from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from gtfs_sample import GTFS_info# Experimental code
from distance import get_distance# Experimental code
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
#from google.cloud import storage
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.transit import gtfs_realtime_pb2 #Experimental code
from math import sin, cos, sqrt, atan2, radians, inf
from google.cloud import datastore


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

#config 511.org
token_id = 'ccea4143-8013-4c3e-b3ac-40cf27125f15'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

#config firestore
# Use the application default credentials
cred = credentials.Certificate('firestoredemo-c3174-02794d56d4e5.json')
firebase_admin.initialize_app(cred)

#config datastore
def create_client(project_id):
    return datastore.Client(project_id)

def get_client():
    return datastore.Client(current_app.config['datastoredemo-234300'])
create_client('datastoredemo-234300')
datastore_client = datastore.Client()

db = firestore.client()



@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')



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
        #-------------------Experimental code(start)----------------------------#
        xm = (start_lat + end_lat)/2;
        ym = (start_lng + end_lng)/2;
        mid_loc = {'lat': xm, 'lng': ym};
        radii = get_distance(start_lat, start_lng, xm, ym)
        print('radii ', radii)
        information = GTFS_info()
        print('length before ', len(information))
        updated_info = {}
        for k,v in information.items():
            x1 = v[0]
            y1 = v[1]
            candidate = get_distance(xm, ym, x1, y1)
            print('candidate distance ', candidate)
            print('radii', radii)
            if candidate > radii:
                print('Yes')
                t = int(k)
                updated_info[t] = v
        print('updated len ', len(updated_info))
        #session['bus_dict'] = updated_info
        min = 100000000.0
        for k,v in updated_info.items():
            xi = v[0]
            yi = v[1]
            candidatei = get_distance(start_lat, start_lng, xi, yi)
            print('candidate distance I ', candidatei)
            if candidatei < min:
                min = candidatei
        print("min ", min)
        final_value = {}
        for k,v in updated_info.items():
            xii = v[0]
            yii = v[1]
            candidateii = get_distance(start_lat, start_lng, xii, yii)
            print("cand", candidateii)
            if candidateii == min:
                final_value[k] = v
        print("selected ", final_value)
        #temp_json = json.dumps(updated_info)
        #json_information = json.loads(temp_json)
        #print('JSON', temp_json)
        #temp_loc = information['1210']
        #session['temp_lat'] = temp_loc[0]
        #session['temp_lng'] = temp_loc[1]
        #-------------------Experimental code(end)----------------------------#
        #return render_template('dashboard.html', form=form)
        #return redirect(url_for('what'))#don't miss it.
        print('tyepjhg', type(final_value))
        #print(updated_info)
        return render_template('what.html', data=final_value)
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
            #--------------------------MySql------------------------------------------------------------------#
            #create Cursor
            #//cur = mysql.connection.cursor()
            #//cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))
            #commit to DB
            #//mysql.connection.commit()
            #close the connection
            #//cur.close()
            #-------------------------MySql-----------------------------------------------------------------#

            #------------------------Firestore--------------------------------------------------------------#
            #//doc_ref = db.collection(u'users').document(username)
            #//doc_ref.set({
                #//u'name': name,
                #//u'email': email,
                #//u'username': username,
                #//u'password': password
            #//})
            #------------------------Firestore--------------------------------------------------------------#
            #------------------------datastore--------------------------------------------------------------#
            add_user(name, email, username, password)
            #------------------------datastore--------------------------------------------------------------#
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


        #------------------------MySql--------------------------------------------------#
        #create Cursor
        #//cur = mysql.connection.cursor()

        #get user by Username
        #//result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        #//if result > 0:
            #Get stored hash
            #//data = cur.fetchone()
            #//password = data['password']

            #compare Passwords
            #//if sha256_crypt.verify(password_candidate, password):
                #Passed
                #//session['logged_in'] = True
                #//session['username'] = username
                #//flash('you are now logged in', 'success')
                #//return redirect(url_for('dashboard'))


            #//else:
                #//error = 'Invalid Login'
                #//return render_template('login.html', error=error)
            # Close connection
            #//cur.close()
        #//else:
            #//error = 'Username not found'
            #//return render_template('login.html', error=error)
        #-------------------MySql-------------------------------------#

        #-------------------firestore-------------------------------------#
        #//users_ref = db.collection(u'users')
        #//docs = users_ref.get()
        #//for doc in docs:
            #//doc_dict = doc.to_dict();
            #//if doc_dict['username'] == username:
                #//print('User exist!!')
                #//password = doc_dict['password']
                #//if sha256_crypt.verify(password_candidate, password):
                    #Passed
                    #//print('Password Matched')
                    #//session['logged_in'] = True
                    #//session['username'] = username
                    #//flash('you are now logged in', 'success')
                    #//return redirect(url_for('dashboard'))
                #//else:
                    #//error = 'Invalid Login'
                    #//return render_template('login.html', error=error)

        #//error = 'Username not found'
        #//return render_template('login.html', error=error)

        #-------------------firestore-------------------------------------#
        #-------------------datastore-------------------------------------#
        print('Username', username)
        query = datastore_client.query(kind='username')
        results = list(query.fetch())
        for result in results:
            if result['username'] == username:
                print('User exist')
                password = result['password']
                if sha256_crypt.verify(password_candidate, password):
                #Passed
                    print('Password Matched')
                    session['logged_in'] = True
                    session['username'] = username
                    flash('you are now logged in', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error= 'Invalid login'
                    return render_template('login.html', error=error)
        error = 'Username not found'
        return render_template('login.html', error=error)
        #-------------------datastore-------------------------------------#
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


def add_user(name, email, username, password):
    entity = datastore.Entity(key=datastore_client.key('username'))
    entity.update({
        'name': name,
        'email': email,
        'username': username,
        'password': password
    })
    datastore_client.put(entity)





if __name__ == '__main__':
    app.run(debug=True)
