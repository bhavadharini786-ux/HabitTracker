from flask import Flask
from .utils.db import init_db
from .routes.auth_routes import auth_bp
from .routes.habit_routes import habit_bp
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)

    # 🔐 Load environment variables
    load_dotenv()

    # 🔐 Secure secret key
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret")

    # 🔐 MongoDB config (optional but recommended)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # 🔐 Security settings
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = False  # 🔁 Set True in production (Render)
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # ✅ Initialize DB
    init_db(app)

    # ✅ Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(habit_bp)

    return app