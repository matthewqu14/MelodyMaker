import re, os, datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from audio2midi.audio2midi import main
import subprocess

from helpers import apology, login_required, allowed_file

# Configure application
app = Flask(__name__)
app.config.from_pyfile("config.cfg")

# Set up flask mail
mail = Mail(app)
s = URLSafeTimedSerializer("Thisisasecret!")

# variables
UPLOAD_FOLDER = './audio2midi/input'
tempid = ""

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
# Create 2 tables for users and their audio files
db = SQL("sqlite:///users.db")
db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            hash TEXT NOT NULL,
            confirmation BOOLEAN DEFAULT false);""")
db.execute("""CREATE TABLE IF NOT EXISTS audio (
                user_id INTEGER,
                audio_url TEXT NOT NULL,
                time DATETIME NOT NULL);""")


@app.before_request
def make_session_permanent():
    session.permanent = True


# Homepage for website
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


# HTML for the final page displaying sheet music
@app.route("/render")
@login_required
def render():
    return render_template("sheetmusic.html")


# Login functionality from Finance
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

        # Error check to see if user confirmed email
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


# Logout functionality from Finance
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
    now = datetime.datetime.now()
    if request.method == 'POST':
        # Checks if the post request has the file part
        if 'file' not in request.files:
            flash('No file part.')
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            flash('Please select a file.')
            return redirect(request.url)
        # Saves file to the input folder in audio2midi
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
                    os.environ['Muse'],
                    "-o",
                    songname + ".musicxml",
                    songname + ".mid"
                ]
            )
            os.chdir("./../..")
            # Enters .wav file into a database for each user to keep track of saved audio files.
            db.execute("INSERT INTO audio (user_id, audio_url, time) VALUES (?, ?, ?)", session['user_id'],
                       file.filename, now.strftime("%Y-%m-%d %H:%M:%S"))
            return redirect("/render")
        else:
            # Error checking for non-wav files.
            flash("Please select a .wav file.")
            return redirect("/myaudio")
    else:
        # If page reached via GET, displays table of saved audio tracks
        rows = db.execute("SELECT * FROM audio WHERE user_id = ?", session['user_id'])
        filtered_rows = []
        [filtered_rows.append(row) for row in rows if row not in filtered_rows]
        return render_template("myaudio.html", rows=filtered_rows, id=session['user_id'])


# Register functionality from Finance
@app.route("/register", methods=["GET", "POST"])
def register():
    # Register user
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Error checking for no username
        username = request.form.get("username")
        if not username:
            flash("Please enter a username.")
            return redirect("/register")

        # Error checking for no password
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            flash("Please enter a password.")
            return redirect("/register")

        # Error checking for password not meeting requirements
        if len(password) < 8 or (not re.search("\W|_", password)) or (not re.search("[A-Z]", password)):
            flash("Password does not meet requirements.")
            return redirect("/register")

        # Error checking for passwords not matching
        if password != confirmation:
            flash("Passwords do not match.")
            return redirect("/register")

        # Error checking for username already existing in database
        username_exist = db.execute("SELECT COUNT(*) FROM users WHERE username = ?", username)
        if username_exist[0]["COUNT(*)"] != 0:
            flash("Username already taken.")
            return redirect("/register")

        # Sends email with custom URL to user
        token = s.dumps(username, salt="confirm")
        msg = Message("Confirm Your MelodyMaker Account", sender='melodymakerpro@gmail.com', recipients=[username])
        link = url_for("confirm", token=token, _external=True)
        msg.body = "Verify your MelodyMaker Account by clicking on the link below. " \
                   "Please be aware that this link will expire in 20 minutes; " \
                   "afterwards, you will have to register your account again.\n\n{}".format(link)
        try:
            mail.send(msg)
        except:
            # Error checking for username that isn't in an email format.
            flash("Sorry! That doesn't look like an email.")
            return redirect("/register")

        # Enters in username and password hash into database, but keeps confirmation defaulted to FALSE
        # While confirmation is FALSE, user cannot login still.
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Global variable used to reference in confirm(token) function
        global tempid
        tempid = rows[0]["id"]
        return render_template("confirmation.html", token=token, email=username)


@app.route('/confirm/<token>')
def confirm(token):
    global tempid
    try:
        s.loads(token, salt="confirm", max_age=1200)
    except SignatureExpired:
        # If url has expired, the username and password is deleted from the database
        db.execute("DELETE FROM users WHERE id = ?", tempid)
        flash("Your link has expired. Please register your account again.")
        session["user_id"] = None
        return redirect("/register")

    # If user confirms email, confirmation is set to TRUE so user can login.
    db.execute("UPDATE users SET confirmation = ? WHERE id = ?", 1, tempid)
    session["user_id"] = tempid
    return render_template("welcome.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology("Internal Server Error")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
