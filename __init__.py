import os
from flask import Flask
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
    jwt = JWTManager(app)
    CORS(app)  # allow frontend requests

    # =========================
    # 🔧 Register Blueprints
    # =========================
    from app.routes.auth_routes import auth_bp
    from app.routes.habit_routes import habit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(habit_bp)

    return app

