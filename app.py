import re, os

import sqlite3
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from audio2midi.audio2midi import main
import subprocess

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
app.config.from_pyfile("config.cfg")

mail = Mail(app)

s = URLSafeTimedSerializer("Thisisasecret!")

tempid = ""

# variables
UPLOAD_FOLDER = './audio2midi/input'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")
db2 = SQL("sqlite:///audio.db")
db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            hash TEXT NOT NULL,
            confirmation BOOLEAN DEFAULT false);""")
db2.execute("""CREATE TABLE IF NOT EXISTS audio (
                user_id INTEGER,
                audio_url TEXT NOT NULL,
                time DATETIME NOT NULL);""")


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter a username.")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter a password.")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password.")
            return render_template("login.html")

        if not rows[0]["confirmation"]:
            flash("You have not yet confirmed your email address.")
            return render_template("login.html")
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("You have successfully logged in.")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        session.clear()
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to homepage
    flash("You have successfully logged out.")
    return redirect("/")


@app.route("/myaudio", methods=["GET", "POST"])
@login_required
def myaudio():
    if request.method == "POST":
        return apology("TODO")
    else:
        db2.execute("INSERT INTO audio (user_id, audio_url) VALUES (?, ?)", session['user_id'],
                    "C:\\Users\\matth\\Music\\C5")
        rows = db2.execute("SELECT * FROM audio WHERE user_id = ?", session['user_id'])
        return render_template("myaudio.html", rows=rows, id=session['user_id'])


@app.route("/mysheet", methods=["GET", "POST"])
@login_required
def mysheet():
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        if not username:
            flash("Please enter a username.")
            return redirect("/register")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            flash("Please enter a password.")
            return redirect("/register")
        if len(password) < 8 or (not re.search("\W|_", password)) or (not re.search("[A-Z]", password)):
            flash("Password does not meet requirements.")
            return redirect("/register")
        if password != confirmation:
            flash("Passwords do not match.")
            return redirect("/register")
        username_exist = db.execute("SELECT COUNT(*) FROM users WHERE username = ?", username)
        if username_exist[0]["COUNT(*)"] != 0:
            flash("Username already taken.")
            return redirect("/register")
        token = s.dumps(username, salt="confirm")
        msg = Message("Confirm Your MelodyMaker Account", sender='melodymakerpro@gmail.com', recipients=[username])
        link = url_for("confirm", token=token, _external=True)
        msg.body = "Verify your MelodyMaker Account by clicking on the link below. " \
                   "Please be aware that this link will expire in 20 minutes; " \
                   "afterwards, you will have to register your account again.\n\n{}".format(link)
        try:
            mail.send(msg)
        except:
            flash("Sorry! That doesn't look like an email.")
            return redirect("/register")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        global tempid
        tempid = rows[0]["id"]
        return render_template("confirmation.html", token=token, email=username)


@app.route('/confirm/<token>')
def confirm(token):
    global tempid
    try:
        s.loads(token, salt="confirm", max_age=1200)
    except SignatureExpired:
        db.execute("DELETE FROM users WHERE id = ?", tempid)
        flash("Your link has expired. Please register your account again.")
        session["user_id"] = None
        return redirect("/register")
    db.execute("UPDATE users SET confirmation = true WHERE id = ?", tempid)
    session["user_id"] = tempid
    return render_template("welcome.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/audio', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            songname = filename.split('.wav')[0]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            main('./audio2midi/input/' + filename,
                 './audio2midi/model/model_melody',
                 './audio2midi/output/' + songname)
            os.chdir("./audio2midi/output")
            subprocess.check_call(
                [
                    "C:\\Program Files\\MuseScore 3\\bin\\MuseScore3.exe",
                    "-o",
                    songname + ".musicxml",
                    songname + ".mid"
                ]
            )
            os.chdir("./../..")
            return '''
            <html>
            <head>
                <title> OSMD Raw Javascript Usage Example </title>
            </head>
            <body>
            
            <script src="static/opensheetmusicdisplay.min.js"></script> <!-- you need to provide the .js file, see README.md-->
            <div id="osmdCanvas"/>
            
            <input type="file" id="files" name="files[]" multiple />
            <output id="list"></output>
            
            <script src="static/fileSelectAndLoadOSMD.js"></script>
            
            </body>
            </html>
            '''
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology("Internal Server Error")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
