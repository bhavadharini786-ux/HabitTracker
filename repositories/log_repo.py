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
# 🔍 FIND LOG
# =========================
def find_log(user, habit_id, date_str):
    oid = safe_objectid(habit_id)
    if not oid:
        return None
    return mongo.db.logs.find_one({
        "user": user,
        "habit_id": oid,
        "date": date_str  # YYYY-MM-DD
    })


# =========================
# ➕ CREATE LOG
# =========================
def create_log(user, habit_id, date_str):
    oid = safe_objectid(habit_id)
    if not oid:
        return None

    now = datetime.utcnow().isoformat(timespec="seconds")
    return mongo.db.logs.insert_one({
        "user": user,
        "habit_id": oid,
        "date": date_str,       # YYYY-MM-DD
        "timestamp": now,       # full ISO timestamp
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
def toggle_log(user, habit_id, date_str):
    oid = safe_objectid(habit_id)
    if not oid:
        raise ValueError("Invalid habit id")

    existing = mongo.db.logs.find_one({
        "user": user,
        "habit_id": oid,
        "date": date_str
    })

    if existing:
        mongo.db.logs.delete_one({"_id": existing["_id"]})
        return False  # unchecked
    else:
        now = datetime.utcnow().isoformat(timespec="seconds")
        mongo.db.logs.insert_one({
            "user": user,
            "habit_id": oid,
            "date": date_str,
            "timestamp": now,
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
def get_logs_by_date(user, date_str):
    return list(mongo.db.logs.find({
        "user": user,
        "date": date_str
    }))