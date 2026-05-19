from functools import wraps
from flask import session, redirect, url_for


# =========================
# 🔐 LOGIN REQUIRED DECORATOR
# =========================
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Check if user logged in
        if "user" not in session:
            return redirect(url_for("auth.login"))

        # Continue route normally
        return f(*args, **kwargs)

    return decorated_function