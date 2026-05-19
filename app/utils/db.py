from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    print("MONGO_URI =", app.config.get("MONGO_URI"))
    mongo.init_app(app)