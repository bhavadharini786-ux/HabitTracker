from datetime import date, datetime
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
    return habit_repo.create_habit(user, name, time)

def toggle_habit(user, habit_id):
    today = str(date.today())
    oid = ObjectId(habit_id)

    habit = mongo.db.habits.find_one({"_id": oid, "user": user})
    if not habit:
        return None

    existing = mongo.db.logs.find_one({
        "habit_id": oid,
        "user": user,
        "date": today
    })

    if existing:
        # Undo completion for today
        mongo.db.logs.delete_one({"_id": existing["_id"]})
        return {"completed": False, "streak": habit.get("streak", 0), "last_completed": habit.get("last_completed")}

    # Mark complete
    now = datetime.utcnow().isoformat(timespec="seconds")
    mongo.db.logs.insert_one({
        "habit_id": oid,
        "user": user,
        "date": today,
        "completed": True,
        "timestamp": now
    })

    new_streak = habit.get("streak", 0) + 1
    mongo.db.habits.update_one(
        {"_id": oid, "user": user},
        {"$set": {"streak": new_streak, "last_completed": now}}
    )

    return {"completed": True, "streak": new_streak, "last_completed": now}
