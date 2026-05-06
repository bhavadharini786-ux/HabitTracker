from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import mongo

auth_bp = Blueprint("auth", __name__)


# ==========================
# 🔐 LOGIN
# ==========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = mongo.db.users.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user"] = {
                "email": email,
                "id": str(user["_id"])
            }

            return redirect(url_for("habit.dashboard"))

        flash("Invalid email or password")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# ==========================
# 🆕 SIGNUP
# ==========================
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # 🔐 PASSWORD VALIDATION
        if len(password) < 6:
            flash("Password must be at least 6 characters")
            return redirect(url_for("auth.signup"))

        if not any(char.isdigit() for char in password):
            flash("Password must include at least one number")
            return redirect(url_for("auth.signup"))

        if not any(char.isupper() for char in password):
            flash("Password must include at least one uppercase letter")
            return redirect(url_for("auth.signup"))

        # 🔁 Check existing user
        if mongo.db.users.find_one({"email": email}):
            flash("User already exists")
            return redirect(url_for("auth.signup"))

        # ✅ Save user
        mongo.db.users.insert_one({
            "email": email,
            "password": generate_password_hash(password)
        })

        flash("Account created successfully! Please login")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


# ==========================
# 🚪 LOGOUT
# ==========================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


