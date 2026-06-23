from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, date, timedelta
import calendar
from app.utils.db import mongo

habit_bp = Blueprint("habit", __name__)

# -------------------------
# 📊 DASHBOARD API
# -------------------------
@habit_bp.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard_api():
    user = get_jwt_identity()
    today = datetime.utcnow().date().isoformat()

    habits = list(mongo.db.habits.find({"user": user}).sort("order_index", 1))
    logs_today = list(mongo.db.logs.find({"user": user, "date": today}))

    total = len(habits)
    completed = len(logs_today)
    remaining = total - completed
    completion_percent = int((completed / total) * 100) if total > 0 else 0

    # streak calculation
    streak = 0
    for i in range(365):
        d = (datetime.utcnow().date() - timedelta(days=i)).isoformat()
        if mongo.db.logs.count_documents({"user": user, "date": d}) > 0:
            streak += 1
        else:
            break

    return jsonify({
        "habits": [{"id": str(h["_id"]), "name": h["name"], "time": h.get("time")} for h in habits],
        "today_count": completed,
        "remaining": remaining,
        "completion_percent": completion_percent,
        "streak": streak,
        "score": f"{completed}/{total}",
        "timestamp": datetime.utcnow().isoformat(timespec="seconds")
    })

# -------------------------
# ➕ CREATE HABIT
# -------------------------
@habit_bp.route("/api/habit/create", methods=["POST"])
@jwt_required()
def create_habit():
    user = get_jwt_identity()
    data = request.get_json() or {}
    name = data.get("name")
    time_str = data.get("time")

    if not name or not time_str:
        return jsonify({"error": "Missing fields"}), 400

    try:
        habit_time = datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        return jsonify({"error": "Invalid time format, use HH:MM:SS"}), 400

    habit = {
        "user": user,
        "name": name,
        "time": habit_time.strftime("%H:%M:%S"),
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        "streak": 0,
        "last_completed": None,
        "active": True,
        "order_index": mongo.db.habits.count_documents({"user": user})
    }
    mongo.db.habits.insert_one(habit)
    return jsonify({"message": "Habit created", "habit": habit}), 201

# -------------------------
# 🔄 TOGGLE / UPDATE HABIT
# -------------------------
@habit_bp.route("/api/habit/update/<habit_id>", methods=["PUT"])
@jwt_required()
def update_habit(habit_id):
    user = get_jwt_identity()
    try:
        oid = ObjectId(habit_id)
    except:
        return jsonify({"error": "Invalid habit id"}), 400

    habit = mongo.db.habits.find_one({"_id": oid, "user": user})
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    today = datetime.utcnow().date().isoformat()
    log = mongo.db.logs.find_one({"user": user, "habit_id": oid, "date": today})

    if log:
        # Undo completion
        mongo.db.logs.delete_one({"_id": log["_id"]})
        return jsonify({"completed": False, "streak": habit.get("streak", 0), "last_completed": None})
    else:
        # Mark complete
        now = datetime.utcnow().isoformat(timespec="seconds")
        mongo.db.logs.insert_one({
            "habit_id": oid,
            "user": user,
            "date": today,
            "completed": True,
            "timestamp": now
        })
        streak = habit.get("streak", 0) + 1
        mongo.db.habits.update_one({"_id": oid}, {"$set": {"streak": streak, "last_completed": now}})
        return jsonify({"completed": True, "streak": streak, "last_completed": now})

# -------------------------
# 🔁 COMPLETE HABIT (explicit endpoint)
# -------------------------
@habit_bp.route("/api/habit/complete/<habit_id>", methods=["POST"])
@jwt_required()
def complete_habit(habit_id):
    user = get_jwt_identity()
    today = datetime.utcnow().date().isoformat()
    now = datetime.utcnow().isoformat(timespec="seconds")
    oid = ObjectId(habit_id)

    mongo.db.logs.update_one(
        {"habit_id": oid, "user": user, "date": today},
        {"$set": {"completed": True, "timestamp": now}},
        upsert=True
    )
    mongo.db.habits.update_one({"_id": oid, "user": user}, {"$inc": {"streak": 1}})
    return jsonify({"message": "Habit marked complete", "timestamp": now})

# -------------------------
# 📅 TODAY HABITS
# -------------------------
@habit_bp.route("/api/habits/today", methods=["GET"])
@jwt_required()
def today_habits():
    user = get_jwt_identity()
    today = datetime.utcnow().date().isoformat()
    habits = list(mongo.db.habits.find({"user": user}).sort("order_index", 1))

    logs = list(mongo.db.logs.find({"user": user, "date": today}))
    completed = {str(l["habit_id"]) for l in logs}

    return jsonify([
        {
            "id": str(h["_id"]),
            "name": h["name"],
            "time": h.get("time"),
            "completed": str(h["_id"]) in completed
        }
        for h in habits
    ])

# -------------------------
# ❌ DELETE HABIT
# -------------------------
@habit_bp.route("/api/habit/delete/<habit_id>", methods=["DELETE"])
@jwt_required()
def delete_habit(habit_id):
    user = get_jwt_identity()
    oid = ObjectId(habit_id)
    mongo.db.habits.delete_one({"_id": oid, "user": user})
    mongo.db.logs.delete_many({"habit_id": oid, "user": user})
    return jsonify({"message": "Habit deleted"})

# -------------------------
# ✏️ EDIT HABIT
# -------------------------
@habit_bp.route("/habit/edit/<habit_id>", methods=["GET"])
def edit_habit_page(habit_id):
    try:
        oid = ObjectId(habit_id)
    except:
        return "Invalid habit id", 400

    habit = mongo.db.habits.find_one({"_id": oid})
    if not habit:
        return "Habit not found", 404

    habit["_id"] = str(habit["_id"])
    if "time" in habit and habit["time"]:
        try:
            habit["time"] = datetime.strptime(habit["time"], "%H:%M:%S").strftime("%H:%M:%S")
        except:
            habit["time"] = str(habit["time"])

    return render_template("edit_habit.html", habit=habit)

@habit_bp.route("/api/habit/edit/<habit_id>", methods=["POST"])
@jwt_required()
def edit_habit(habit_id):
    user = get_jwt_identity()
    try:
        oid = ObjectId(habit_id)
    except:
        return jsonify({"error": "Invalid habit id"}), 400

    data = request.get_json() or {}
    update_fields = {}

    if "name" in data:
        update_fields["name"] = data["name"]

    if "time" in data:
        try:
            habit_time = datetime.strptime(data["time"], "%H:%M:%S").time()
            update_fields["time"] = habit_time.strftime("%H:%M:%S")
        except ValueError:
            return jsonify({"error": "Invalid time format, must be HH:MM:SS"}), 400

    mongo.db.habits.update_one({"_id": oid, "user": user}, {"$set": update_fields})
    return jsonify({"message": "Habit updated"})

# -------------------------
# 📊 WEEKLY API
# -------------------------
@habit_bp.route("/api/weekly", methods=["GET"])
@jwt_required()
def weekly_api():
    user = get_jwt_identity()
    today = datetime.utcnow().date()

    # Week boundaries (Monday → Sunday)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    # ✅ Sorted by order_index
    habits = list(mongo.db.habits.find({"user": user}).sort("order_index", 1))
    total_habits = len(habits)

    # Logs for this week
    logs = list(mongo.db.logs.find({
        "user": user,
        "date": {"$gte": start.isoformat(), "$lte": end.isoformat()}
    }))

    # Map of completed counts per day
    log_map = {}
    for log in logs:
        log_map[log["date"]] = log_map.get(log["date"], 0) + 1

    # Daily breakdown
    days = []
    for i in range(7):
        d = (start + timedelta(days=i)).isoformat()
        days.append({
            "date": d + "T00:00:00",
            "count": log_map.get(d, 0)
        })

    # Streak calculation (backwards from today)
    streak = 0
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        if mongo.db.logs.count_documents({"user": user, "date": d}) > 0:
            streak += 1
        else:
            break

    # Consistency percentage
    total_completed = len(logs)
    total_possible = total_habits * 7
    consistency = int((total_completed / total_possible) * 100) if total_possible else 0

    # ✅ Habit performance stats
    habit_counts = {}
    for log in logs:
        hid = str(log["habit_id"])
        habit_counts[hid] = habit_counts.get(hid, 0) + 1

    habit_stats = [
        {"name": h["name"], "count": habit_counts.get(str(h["_id"]), 0)}
        for h in habits
    ]

    return jsonify({
        "week_start": start.isoformat() + "T00:00:00",
        "week_end": end.isoformat() + "T00:00:00",
        "days": days,
        "streak": streak,
        "consistency": consistency,
        "habit_stats": habit_stats
    })

# -------------------------
# 
# -------------------------
# 📅 MONTHLY API
# -------------------------
@habit_bp.route("/api/monthly", methods=["GET"])
@jwt_required()
def monthly_api():
    user = get_jwt_identity()
    month_offset = int(request.args.get("monthOffset", 0))

    today = datetime.utcnow().date()
    target_month = today.month + month_offset
    target_year = today.year

    while target_month < 1:
        target_month += 12
        target_year -= 1
    while target_month > 12:
        target_month -= 12
        target_year += 1

    num_days = calendar.monthrange(target_year, target_month)[1]
    days, total_completions, missed_days = [], 0, 0

    for d in range(1, num_days + 1):
        date_str = date(target_year, target_month, d).isoformat()
        count = mongo.db.logs.count_documents({"user": user, "date": date_str})
        days.append({"date": date_str + "T00:00:00", "count": count})
        total_completions += count
        if count == 0:
            missed_days += 1

    completion_rate = int((sum(1 for day in days if day["count"] > 0) / num_days) * 100)

    # ✅ streak calculation should finish before returning
    streak = 0
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        if mongo.db.logs.count_documents({"user": user, "date": d}) > 0:
            streak += 1
        else:
            break

    return jsonify({
        "month_name": date(target_year, target_month, 1).strftime("%B %Y"),
        "days": days,
        "total_completions": total_completions,
        "completion_rate": completion_rate,
        "streak": streak,
        "missed_days": missed_days,
        "timestamp": datetime.utcnow().isoformat(timespec="seconds")
    })

    
    
    
@habit_bp.route("/api/analytics", methods=["GET"])
@jwt_required()
def analytics_api():
    user = get_jwt_identity()
    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"user": user}))

    today = datetime.utcnow().date()
    logs_map = {}
    for log in logs:
        d = log["date"] if isinstance(log["date"], str) else log["date"].isoformat()
        logs_map[d] = logs_map.get(d, 0) + 1

    # Weekly trend (last 7 days)
    weekly_labels = []
    weekly_trend = []
    for i in range(6, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        weekly_labels.append(d + "T00:00:00")
        weekly_trend.append(logs_map.get(d, 0))

    # Completion rate (last 7 days)
    total_habits = len(habits)
    total_completed = sum(weekly_trend)
    total_possible = total_habits * 7
    completion_rate = int((total_completed / total_possible) * 100) if total_possible else 0

    # Streak
    streak = 0
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        if logs_map.get(d, 0) > 0:
            streak += 1
        else:
            break

    # Habit performance
    habit_counts = {}
    for log in logs:
        hid = str(log["habit_id"])
        habit_counts[hid] = habit_counts.get(hid, 0) + 1

    habit_stats = [{"name": h["name"], "count": habit_counts.get(str(h["_id"]), 0)} for h in habits]

    # Top habit
    top_habit = None
    if habit_stats:
        top_habit = max(habit_stats, key=lambda h: h["count"])["name"]

    # Last 30 days heatmap
    heatmap = []
    missed_days = 0
    for i in range(29, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        count = logs_map.get(d, 0)
        intensity = 0
        if count >= 1 and count <= 2:
            intensity = 1
        elif count >= 3 and count <= 5:
            intensity = 2
        elif count > 5:
            intensity = 3
        else:
            missed_days += 1
        heatmap.append({"date": d + "T00:00:00", "count": count, "intensity": intensity})

    return jsonify({
        "completion_rate": completion_rate,
        "streak": streak,
        "top_habit": top_habit,
        "weekly_labels": weekly_labels,
        "weekly_trend": weekly_trend,
        "habit_stats": habit_stats,
        "heatmap": heatmap,
        "missed_days": missed_days,
        "timestamp": datetime.utcnow().isoformat(timespec="seconds")
    })
