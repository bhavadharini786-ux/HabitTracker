from flask import Blueprint, request, jsonify, session
from app.utils.db import mongo
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.utils.auth import login_required

# =========================
# ✅ BLUEPRINT (FIXED)
# =========================
habit_bp = Blueprint("habit", __name__)


# =========================
# 🔐 SAFE OBJECTID
# =========================
def safe_objectid(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


# =========================
# 👤 GET CURRENT USER EMAIL
# =========================
def get_user_email():
    return session.get("user", {}).get("email")


# =========================
# 📊 GET WEEK DATA
# =========================
@habit_bp.route("/<habit_id>/week", methods=["GET"])
@login_required
def get_week(habit_id):

    oid = safe_objectid(habit_id)
    if not oid:
        return jsonify({"error": "Invalid habit id"}), 400

    habit = mongo.db.habits.find_one({
        "_id": oid,
        "user": get_user_email()
    })

    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    return jsonify({
        "name": habit.get("name"),
        "weekly_data": habit.get("weekly_data", [0] * 7)
    })


# =========================
# ✏ UPDATE DAY
# =========================
@habit_bp.route("/<habit_id>/day", methods=["PATCH"])
@login_required
def update_day(habit_id):

    oid = safe_objectid(habit_id)
    if not oid:
        return jsonify({"error": "Invalid habit id"}), 400

    body = request.get_json() or {}

    day = body.get("day")
    value = body.get("value")

    if day is None or value is None:
        return jsonify({"error": "Missing fields"}), 400

    if not isinstance(day, int) or day not in range(7):
        return jsonify({"error": "Invalid day index"}), 400

    if value not in [0, 0.5, 1]:
        return jsonify({"error": "Invalid value"}), 400

    habit = mongo.db.habits.find_one({
        "_id": oid,
        "user": get_user_email()
    })

    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    weekly_data = habit.get("weekly_data") or [0] * 7
    weekly_data[day] = value

    mongo.db.habits.update_one(
        {"_id": oid},
        {"$set": {"weekly_data": weekly_data}}
    )

    return jsonify({
        "message": "Day updated",
        "weekly_data": weekly_data
    })


# =========================
# 🔥 STREAK
# =========================
def calculate_streak(data):
    streak = 0
    for v in reversed(data):
        if v > 0:
            streak += 1
        else:
            break
    return streak


# =========================
# 📈 WEEKLY STATS
# =========================
@habit_bp.route("/<habit_id>/stats", methods=["GET"])
@login_required
def weekly_stats(habit_id):

    oid = safe_objectid(habit_id)
    if not oid:
        return jsonify({"error": "Invalid habit id"}), 400

    habit = mongo.db.habits.find_one({
        "_id": oid,
        "user": get_user_email()
    })

    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    data = habit.get("weekly_data") or [0] * 7

    streak = calculate_streak(data)
    score = sum(1 for v in data if v > 0)

    return jsonify({
        "streak": streak,
        "weekly_score": f"{score}/7",
        "weekly_data": data
    })