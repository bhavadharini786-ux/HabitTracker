from functools import wraps
from flask import session, redirect, url_for, jsonify, request


# =========================
# 🔐 PAGE LOGIN REQUIRED
# =========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Debug (optional)
        # print("SESSION:", session)

        if "user" not in session:
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


# =========================
# 🔐 API LOGIN REQUIRED
# =========================
def api_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        # Debug (optional)
        # print("API SESSION:", session)

        if "user" not in session:
            return jsonify({
                "error": "Unauthorized",
                "message": "Please login first"
            }), 401

        return f(*args, **kwargs)

    return wrapper


# =========================
# 🔐 OPTIONAL: FLEXIBLE DECORATOR
# (AUTO detect API vs PAGE)
# =========================
def smart_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user" not in session:

            # If API call (JSON / fetch)
            if request.path.startswith("/habit/api") or request.is_json:
                return jsonify({
                    "error": "Unauthorized"
                }), 401

            # Otherwise normal page
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return wrapper