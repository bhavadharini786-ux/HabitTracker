from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import mongo
import re

auth_bp = Blueprint("auth", __name__)

# ==========================
# 🔐 LOGIN
# ==========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # If already logged in
    if "user" in session:
        return redirect(url_for("habit.dashboard"))

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        # ✅ Validation
        if not email or not password:
            flash("All fields are required")
            return redirect(url_for("auth.login"))

        # ✅ Find user
        user = mongo.db.users.find_one({"email": email})

        # ✅ Check password
        if user and check_password_hash(user["password"], password):

            session.clear()
            session["user"] = {
                "email": email
            }

            flash("Login successful")
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

        email = request.form["email"].strip()
        password = request.form["password"]

        # ✅ Validation
        if not email or not password:
            flash("All fields are required")
            return redirect(url_for("auth.signup"))

        # ✅ Email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format")
            return redirect(url_for("auth.signup"))

        # ✅ Password validation
        if len(password) < 6:
            flash("Password must be at least 6 characters")
            return redirect(url_for("auth.signup"))

        # ✅ Check existing user
        existing_user = mongo.db.users.find_one({"email": email})

        if existing_user:
            flash("User already exists")
            return redirect(url_for("auth.signup"))

        # ✅ Create user
        mongo.db.users.insert_one({
            "email": email,
            "password": generate_password_hash(password)
        })

        flash("Account created successfully")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


# ==========================
# 🚪 LOGOUT
# ==========================
@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully")

    return redirect(url_for("auth.login"))
