from flask import Flask
from dotenv import load_dotenv
import os

from .utils.db import init_db
from .routes.auth_routes import auth_bp
from .routes.habit_routes import habit_bp


def create_app():

    # ✅ IMPORTANT: explicitly set template folder
    app = Flask(__name__, template_folder="templates")

    load_dotenv()

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    init_db(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(habit_bp, url_prefix="/habit")

    return app