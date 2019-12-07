import re, os

import sqlite3
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from audio2midi.audio2midi import main
import subprocess

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

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
db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            hash TEXT NOT NULL,
            confirmation BOOLEAN DEFAULT false);""")


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter a username.")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter a password.")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("You have successfully logged in.")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to homepage
    flash("You have successfully logged out.")
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
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
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        flash("TODO")
        return redirect("/")


@app.route("/confirmation")
@login_required
def confirmation():
    return render_template


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


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
                 './audio2midi/output/' + songname,
                 170)
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
            return redirect("/audio")
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
