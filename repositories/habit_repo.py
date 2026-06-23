from app.utils.db import mongo
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

def safe_objectid(id_str):
    """Safely convert a string to ObjectId, return None if invalid."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None

def get_habits_by_user(user):
    """Fetch all habits for a given user, sorted by creation time."""
    return list(mongo.db.habits.find({"user": user}).sort("created_at", -1))

def get_habit_by_id(habit_id):
    """Fetch a single habit by its ID."""
    oid = safe_objectid(habit_id)
    if not oid:
        return None
    return mongo.db.habits.find_one({"_id": oid})

def create_habit(user, name, time_str):
    """Create a new habit with default fields."""
    try:
        habit_time = datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        # fallback if only HH:MM provided
        habit_time = datetime.strptime(time_str, "%H:%M").time()

    result = mongo.db.habits.insert_one({
        "user": user,
        "name": name,
        "time": habit_time.isoformat(),   # HH:MM:SS
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        "streak": 0,
        "last_completed": None,
        "completed": False,
        "active": True
    })
    return str(result.inserted_id)

def update_habit(habit_id, data):
    """Update habit fields safely, including time parsing."""
    oid = safe_objectid(habit_id)
    if not oid:
        return False

    if "time" in data:
        try:
            habit_time = datetime.strptime(data["time"], "%H:%M:%S").time()
        except ValueError:
            habit_time = datetime.strptime(data["time"], "%H:%M").time()
        data["time"] = habit_time.isoformat()

    result = mongo.db.habits.update_one({"_id": oid}, {"$set": data})
    return result.modified_count > 0

def delete_habit(habit_id):
    """Delete a habit and cascade delete its logs."""
    oid = safe_objectid(habit_id)
    if not oid:
        return False

    mongo.db.logs.delete_many({"habit_id": oid})
    result = mongo.db.habits.delete_one({"_id": oid})
    return result.deleted_count > 0
