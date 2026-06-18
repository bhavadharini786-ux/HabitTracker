import os
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.utils.db import mongo

def create_app():
    app = Flask(__name__)

    # =========================
    # 🔧 Core Config
    # =========================
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/habitflow")

    # =========================
    # 🔧 Extensions
    # =========================
    mongo.init_app(app)
    JWTManager(app)
    CORS(app)

    # =========================
    # 🔧 Register Blueprints (API routes)
    # =========================
    from app.routes.auth_routes import auth_bp
    from app.routes.habit_routes import habit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(habit_bp)

    # =========================
    # 🔧 Template Routes (Frontend pages)
    # =========================
    @app.route("/", methods=["GET"])
    def home():
        return render_template("home.html")

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/analytics", methods=["GET"])
    def analytics():
        return render_template("analytics.html")

    @app.route("/habits", methods=["GET"])
    def habits():
        return render_template("habits.html")

    @app.route("/weekly", methods=["GET"])
    def weekly():
        return render_template("weekly.html")

    @app.route("/signup", methods=["GET"])
    def signup_page():
        return render_template("signup.html")

    @app.route("/login", methods=["GET"])
    def login_page():
        return render_template("login.html")

    @app.route("/edit_habit", methods=["GET"])
    def edit_habit():
        return render_template("edit_habit.html")

    return app

