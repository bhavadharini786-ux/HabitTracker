from app.utils.db import mongo
from bson import ObjectId
from bson.errors import InvalidId


# =========================
# 🔐 SAFE OBJECTID
# =========================
def safe_objectid(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


# =========================
# 🔍 FIND LOG
# =========================
def find_log(user, habit_id, date):

    oid = safe_objectid(habit_id)
    if not oid:
        return None

    return mongo.db.logs.find_one({
        "user": user,
        "habit_id": oid,
        "date": date
    })


# =========================
# ➕ CREATE LOG
# =========================
def create_log(user, habit_id, date):

    oid = safe_objectid(habit_id)
    if not oid:
        return None

    return mongo.db.logs.insert_one({
        "user": user,
        "habit_id": oid,
        "date": date,
        "completed": True
    })


# =========================
# 🗑 DELETE LOG
# =========================
def delete_log(log_id):

    oid = safe_objectid(log_id)
    if not oid:
        return False

    result = mongo.db.logs.delete_one({"_id": oid})
    return result.deleted_count > 0


# =========================
# 🔄 TOGGLE LOG (SAFE + OPTIMIZED)
# =========================
def toggle_log(user, habit_id, date):

    oid = safe_objectid(habit_id)
    if not oid:
        raise ValueError("Invalid habit id")

    existing = mongo.db.logs.find_one({
        "user": user,
        "habit_id": oid,
        "date": date
    })

    if existing:
        mongo.db.logs.delete_one({"_id": existing["_id"]})
        return False  # unchecked
    else:
        mongo.db.logs.insert_one({
            "user": user,
            "habit_id": oid,
            "date": date,
            "completed": True
        })
        return True   # checked


# =========================
# 📅 GET LOGS BY USER
# =========================
def get_logs_by_user(user):
    return list(mongo.db.logs.find({"user": user}))


# =========================
# 📅 GET LOGS BY DATE
# =========================
def get_logs_by_date(user, date):
    return list(mongo.db.logs.find({
        "user": user,
        "date": date
    }))