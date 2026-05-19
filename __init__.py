
from flask import Flask
from flask_cors import CORS
from app.utils.db import init_db

# IMPORT BLUEPRINTS
from app.routes.habit_routes import habit_bp
from app.routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)

    # ENABLE CORS
    CORS(app)

    app.config["SECRET_KEY"] = "your_secret_key"
    app.config["MONGO_URI"] = "mongodb://localhost:27017/habittracker"

    # INIT DATABASE
    init_db(app)

    # REGISTER BLUEPRINTS
    app.register_blueprint(auth_bp)
    app.register_blueprint(habit_bp)

    @app.route("/")
    def home():
        return "Habit Tracker App Running!"

    return app

