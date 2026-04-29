from flask import Blueprint, request, jsonify
from app.utils.db import mongo
from bson.objectid import ObjectId

habit_bp = Blueprint("habits", __name__)




# ---------------- GET WEEKLY DATA ----------------
@habit_bp.route("/habits/<habit_id>/week", methods=["GET"])
def get_week(habit_id):
    habit = mongo.db.habits.find_one({"_id": ObjectId(habit_id)})

    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    return jsonify({
        "name": habit["name"],
        "weekly_data": habit["weekly_data"]
    })


# ---------------- UPDATE DAY PROGRESS ----------------
@habit_bp.route("/habits/<habit_id>/day", methods=["PATCH"])
def update_day(habit_id):
    body = request.json

    day = body.get("day")        # 0–6
    value = body.get("value")    # 0, 0.5, 1

    if day not in range(7):
        return jsonify({"error": "Invalid day index"}), 400

    habit = mongo.db.habits.find_one({"_id": ObjectId(habit_id)})

    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    weekly_data = habit.get("weekly_data", [0]*7)
    weekly_data[day] = value

    mongo.db.habits.update_one(
        {"_id": ObjectId(habit_id)},
        {"$set": {"weekly_data": weekly_data}}
    )

    return jsonify({"msg": "Day updated", "weekly_data": weekly_data})


# ---------------- STREAK CALCULATION ----------------
def calculate_streak(data):
    streak = 0
    for v in reversed(data):
        if v > 0:
            streak += 1
        else:
            break
    return streak


# ---------------- WEEKLY STATS ----------------
@habit_bp.route("/habits/<habit_id>/stats", methods=["GET"])
def weekly_stats(habit_id):
    habit = mongo.db.habits.find_one({"_id": ObjectId(habit_id)})

    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    data = habit.get("weekly_data", [0]*7)

    streak = calculate_streak(data)
    score = sum(1 for v in data if v > 0)

    return jsonify({
        "streak": streak,
        "weekly_score": f"{score}/7",
        "weekly_data": data
    })