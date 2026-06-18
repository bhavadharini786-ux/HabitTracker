from app.utils.db import mongo
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

def safe_objectid(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None

def get_habits_by_user(user):
    return list(mongo.db.habits.find({"user": user}))

def get_habit_by_id(habit_id):
    oid = safe_objectid(habit_id)
    if not oid:
        return None
    return mongo.db.habits.find_one({"_id": oid})

def create_habit(user, name, time_str):
    habit_time = datetime.strptime(time_str, "%H:%M:%S").time()
    result = mongo.db.habits.insert_one({
        "user": user,
        "name": name,
        "time": habit_time.isoformat(),   # HH:MM:SS
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        "streak": 0,
        "last_completed": None,
        "active": True
    })
    return str(result.inserted_id)

def update_habit(habit_id, data):
    oid = safe_objectid(habit_id)
    if not oid:
        return False
    if "time" in data:
        habit_time = datetime.strptime(data["time"], "%H:%M:%S").time()
        data["time"] = habit_time.isoformat()
    result = mongo.db.habits.update_one({"_id": oid}, {"$set": data})
    return result.modified_count > 0

def delete_habit(habit_id):
    oid = safe_objectid(habit_id)
    if not oid:
        return False
    mongo.db.logs.delete_many({"habit_id": oid})
    result = mongo.db.habits.delete_one({"_id": oid})
    return result.deleted_count > 0
