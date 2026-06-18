from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import mongo
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bson import ObjectId

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# -------------------------
# Signup Page (GET)
# -------------------------
@auth_bp.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

# -------------------------
# Signup Route (POST)
# -------------------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if not username or not email or not password:
        flash("Missing required fields")
        return redirect(url_for("auth.signup_page"))

    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        flash("User already exists")
        return redirect(url_for("auth.signup_page"))

    hashed_pw = generate_password_hash(password)
    mongo.db.users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_pw
    })

    flash("Signup successful! Please login.")
    return redirect(url_for("auth.login_page"))

# -------------------------
# Login Page (GET)
# -------------------------
@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

# -------------------------
# Login Route (POST)
# -------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Missing required fields")
        return redirect(url_for("auth.login_page"))

    user = mongo.db.users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        flash("Invalid credentials")
        return redirect(url_for("auth.login_page"))

    # Issue JWT token
    access_token = create_access_token(identity=str(user["_id"]))

    # Check if user has any habits
    has_habits = mongo.db.habits.count_documents({"user": str(user["_id"])}) > 0

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "new_user": not has_habits
    })


# -------------------------
# Protected Profile Route
# -------------------------
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user["username"],
        "email": user["email"]
    })

