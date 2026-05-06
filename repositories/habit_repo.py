from app.utils.db import mongo
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime


# =========================
# 🔐 SAFE OBJECTID
# =========================
def safe_objectid(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


# =========================
# ➕ CREATE HABIT
# =========================
def create_habit(user, name, time):

    result = mongo.db.habits.insert_one({
        "user": user,
        "name": name,
        "time": time,
        "created_at": datetime.utcnow(),
        "weekly_data": [0] * 7   # Mon → Sun
    })

    return str(result.inserted_id)


# =========================
# 🔍 GET HABIT BY ID
# =========================
def get_habit_by_id(habit_id):

    oid = safe_objectid(habit_id)
    if not oid:
        return None

    return mongo.db.habits.find_one({"_id": oid})


# =========================
# 📋 GET HABITS BY USER
# =========================
def get_habits_by_user(user):

    return list(mongo.db.habits.find({"user": user}))


# =========================
# ✏ UPDATE HABIT
# =========================
def update_habit(habit_id, data):

    oid = safe_objectid(habit_id)
    if not oid:
        return False

    result = mongo.db.habits.update_one(
        {"_id": oid},
        {"$set": data}
    )

    return result.modified_count > 0


# =========================
# 🗑 DELETE HABIT
# =========================
def delete_habit(habit_id):

    oid = safe_objectid(habit_id)
    if not oid:
        return False

    result = mongo.db.habits.delete_one({"_id": oid})
    return result.deleted_count > 0


# =========================
# 📊 COUNT HABITS
# =========================
def count_habits(user):

    return mongo.db.habits.count_documents({"user": user})


# =========================
# 📊 GET HABIT STATS
# =========================
def get_habit_stats(user):

    habits = list(mongo.db.habits.find({"user": user}))

    total = len(habits)

    completed = 0
    for habit in habits:
        if habit.get("done"):   # if you store done flag
            completed += 1

    return {
        "total": total,
        "completed": completed
    }