
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from app.utils.db import init_db

# IMPORT BLUEPRINTS
from app.routes.habit_routes import habit_bp
from app.routes.auth_routes import auth_bp

load_dotenv()

def create_app():
    app = Flask(__name__)

    CORS(app)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # INIT DATABASE
    init_db(app)

    # REGISTER BLUEPRINTS
    app.register_blueprint(auth_bp)
    app.register_blueprint(habit_bp)

    @app.route("/")
    def home():
        return "Habit Tracker App Running!"

    return app










