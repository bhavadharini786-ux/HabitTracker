from flask import Flask

from .config import Config
from .utils.db import init_db

from .routes.auth_routes import auth_bp
from .routes.habit_routes import habit_bp 


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    init_db(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(habit_bp, url_prefix="/habit")

    return app