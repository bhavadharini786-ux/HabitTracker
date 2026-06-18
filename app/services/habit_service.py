from datetime import date
from app.repositories import habit_repo
from app.utils.db import mongo
from bson import ObjectId


SUGGESTED_HABITS = [
    "Drink Water",
    "Exercise",
    "Meditation",
    "Read Book",
    "Walk 5000 Steps",
    "Healthy Diet",
    "Coding Practice",
    "Sleep Early"
]


def get_suggestions():
    return SUGGESTED_HABITS


def create_habit(user, name, time):

    return habit_repo.create_habit(
        user,
        name,
        time
    )


def toggle_habit(user, habit_id):

    today = str(date.today())

    existing = mongo.db.logs.find_one({
        "habit_id": ObjectId(habit_id),
        "user": user,
        "date": today
    })

    if existing:

        mongo.db.logs.delete_one({
            "_id": existing["_id"]
        })

        return False

    mongo.db.logs.insert_one({
        "habit_id": ObjectId(habit_id),
        "user": user,
        "date": today,
        "completed": True
    })

    return True