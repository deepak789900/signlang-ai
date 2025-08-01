from flask import Flask, render_template, redirect, url_for, request, session, Response
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from speechlib import *
from utils import *

# Global variables
name = ''

app = Flask(__name__)
app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Routes
@app.route('/', methods=['GET', 'POST'])
def landing():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    global name
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        con = sqlite3.connect('mydatabase.db')
        cursor = con.cursor()
        cursor.execute("SELECT Name FROM Users WHERE Email=? AND password=?", (email, password))
        try:
            name = cursor.fetchone()[0]
            return redirect(url_for('home'))
        except:
            error = "Invalid Credentials. Please try again."
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST' and request.form['sub'] == 'Submit':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        rpassword = request.form['rpassword']
        pet = request.form['pet']

        if password != rpassword:
            error = 'Passwords do not match.'
            return render_template('register.html', error=error)

        con = sqlite3.connect('mydatabase.db')
        cursor = con.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Users (Date TEXT, Name TEXT, Email TEXT, password TEXT, pet TEXT)")
        cursor.execute("SELECT Name FROM Users WHERE Email=? AND password=?", (email, password))
        if cursor.fetchone():
            error = "User already registered."
        else:
            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            cursor.execute("INSERT INTO Users VALUES (?, ?, ?, ?, ?)", (dt_string, name, email, password, pet))
            con.commit()
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        pet = request.form['pet']
        con = sqlite3.connect('mydatabase.db')
        cursor = con.cursor()
        cursor.execute("SELECT password FROM Users WHERE Email=? AND pet=?", (email, pet))
        password = cursor.fetchone()
        if password:
            error = "Your password: " + password[0]
        else:
            error = "Invalid information. Please try again."
    return render_template('forgot-password.html', error=error)

@app.route('/home')
def home():
    return render_template('home.html', name=name)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', name=name)

@app.route('/video')
def video():
    return render_template('video.html', name=name)

@app.route('/video_stream')
def video_stream():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Disable caching for all responses
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__' and run:
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
