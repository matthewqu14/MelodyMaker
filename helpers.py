from flask import redirect, render_template, session
from functools import wraps

# Variables
ALLOWED_EXTENSIONS = {'wav'}


def apology(message):
    """Render message as an apology to user."""
    return render_template("apology.html", message=message)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """ Checks to see if file is in an accepted format. """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
