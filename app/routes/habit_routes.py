from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify
from app.utils.db import mongo
from app.utils.auth import login_required
from bson import ObjectId
from datetime import datetime, date, timedelta

habit_bp = Blueprint("habit", __name__)


# =========================
# 📊 DASHBOARD PAGE
# =========================
@habit_bp.route("/dashboard")
@login_required
def dashboard():

    user = session.get("user", {}).get("email")
    today = str(date.today())

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"user": user, "date": today}))

    completed_ids = [str(log["habit_id"]) for log in logs]

    return render_template(
        "dashboard.html",
        habits=habits,
        completed_ids=completed_ids,
        today=today
    )


# =========================
# 📊 DASHBOARD API (FIXED)
# =========================
@habit_bp.route("/api/dashboard")
@login_required
def dashboard_api():
    user = session.get("user", {}).get("email")
    today = str(date.today())

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"user": user, "date": today}))

    total = len(habits)
    completed = len(logs)

    return jsonify({
        "total": total,
        "completed": completed
    })


# =========================
# ➕ CREATE HABIT (FIXED USER)
# =========================
@habit_bp.route("/create", methods=["POST"])
@login_required
def create_habit():
    user = session.get("user", {}).get("email")

    mongo.db.habits.insert_one({
        "name": request.form["name"],
        "time": request.form["time"],
        "user": user,  # ✅ FIXED
        "created_at": datetime.utcnow(),
        "weekly_data": [0]*7
    })

    return redirect(url_for("habit.dashboard"))


# =========================
# 📋 VIEW HABITS
# =========================
@habit_bp.route("/habits")
@login_required
def habits():
    user = session.get("user", {}).get("email")
    today = str(date.today())

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"user": user, "date": today}))

    completed_ids = [str(log["habit_id"]) for log in logs]

    return render_template(
        "habits.html",
        habits=habits,
        completed_ids=completed_ids
    )


# =========================
# 🔁 TOGGLE HABIT
# =========================
@habit_bp.route("/toggle/<habit_id>", methods=["POST"])
@login_required
def toggle_habit(habit_id):
    user = session.get("user", {}).get("email")
    today = str(date.today())

    try:
        oid = ObjectId(habit_id)
    except:
        return "Invalid ID", 400

    habit = mongo.db.habits.find_one({"_id": oid})

    if not habit or habit["user"] != user:
        return "Unauthorized", 403

    existing = mongo.db.logs.find_one({
        "habit_id": oid,
        "date": today,
        "user": user
    })

    if existing:
        mongo.db.logs.delete_one({"_id": existing["_id"]})
    else:
        mongo.db.logs.insert_one({
            "habit_id": oid,
            "date": today,
            "completed": True,
            "user": user
        })

    return redirect(url_for("habit.habits"))


# =========================
# ❌ DELETE HABIT
# =========================
@habit_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_habit(id):
    user = session.get("user", {}).get("email")

    try:
        oid = ObjectId(id)
    except:
        return "Invalid ID", 400

    habit = mongo.db.habits.find_one({"_id": oid})

    if not habit or habit["user"] != user:
        return "Unauthorized", 403

    mongo.db.habits.delete_one({"_id": oid})
    mongo.db.logs.delete_many({"habit_id": oid})

    return redirect(url_for("habit.habits"))


# =========================
# ✏️ EDIT HABIT
# =========================
@habit_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_habit(id):
    user = session.get("user", {}).get("email")

    try:
        oid = ObjectId(id)
    except:
        return "Invalid ID", 400

    habit = mongo.db.habits.find_one({"_id": oid})

    if not habit or habit["user"] != user:
        return "Unauthorized", 403

    if request.method == "POST":
        mongo.db.habits.update_one(
            {"_id": oid},
            {"$set": {
                "name": request.form["name"],
                "time": request.form["time"]
            }}
        )
        return redirect(url_for("habit.habits"))

    return render_template("edit_habit.html", habit=habit)


# =========================
# 📊 ANALYTICS PAGE
# =========================
@habit_bp.route("/analytics")
@login_required
def analytics_page():
    return render_template("analytics.html")


# =========================
# 📊 ANALYTICS API (IMPROVED)
# =========================
@habit_bp.route("/api/analytics")
@login_required
def analytics_api():
    user = session.get("user", {}).get("email")

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"user": user}))

    total_habits = len(habits)

    if total_habits == 0:
        return jsonify({
            "completion_rate": 0,
            "streak": 0,
            "top_habit": None,
            "missed_days": 0,
            "weekly_trend": [0]*7,
            "weekly_labels": [],
            "habit_stats": [],
            "heatmap": []
        })

    # -------------------------
    # 🧠 PREP
    # -------------------------
    today = datetime.today()
    logs_map = {}

    for log in logs:
        logs_map.setdefault(log["date"], 0)
        logs_map[log["date"]] += 1

    # -------------------------
    # 📊 WEEKLY DATA
    # -------------------------
    start_week = today - timedelta(days=6)

    week_dates = [
        (start_week + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(7)
    ]

    weekly_trend = [logs_map.get(d, 0) for d in week_dates]

    total_completed = sum(weekly_trend)
    total_possible = total_habits * 7

    completion_rate = int((total_completed / total_possible) * 100)

    # -------------------------
    # 🔥 STREAK (REAL)
    # -------------------------
    streak = 0
    for i in range(365):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if logs_map.get(d, 0) > 0:
            streak += 1
        else:
            break

    # -------------------------
    # 🏆 TOP HABIT + HABIT STATS
    # -------------------------
    habit_counts = {}

    for log in logs:
        hid = str(log["habit_id"])
        habit_counts[hid] = habit_counts.get(hid, 0) + 1

    habit_stats = []

    for habit in habits:
        hid = str(habit["_id"])
        count = habit_counts.get(hid, 0)

        habit_stats.append({
            "name": habit["name"],
            "count": count
        })

    habit_stats.sort(key=lambda x: x["count"], reverse=True)

    top_habit = habit_stats[0]["name"] if habit_stats else None

    # -------------------------
    # ❌ MISSED DAYS (30 days)
    # -------------------------
    start_30 = today - timedelta(days=30)

    all_days_30 = [
        (start_30 + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(31)
    ]

    missed_days = sum(1 for d in all_days_30 if logs_map.get(d, 0) == 0)

    # -------------------------
    # 🟩 MINI HEATMAP (last 30 days)
    # -------------------------
    heatmap = []

    max_count = max(logs_map.values(), default=1)

    def get_intensity(count):
        if max_count == 0:
            return 0
        ratio = count / max_count
        if ratio == 0: return 0
        elif ratio < 0.33: return 1
        elif ratio < 0.66: return 2
        else: return 3

    for d in all_days_30:
        c = logs_map.get(d, 0)
        heatmap.append({
            "date": d,
            "count": c,
            "intensity": get_intensity(c)
        })

    # -------------------------
    # 🚀 RESPONSE
    # -------------------------
    return jsonify({
        "completion_rate": completion_rate,
        "streak": streak,
        "top_habit": top_habit,
        "missed_days": missed_days,
        "weekly_trend": weekly_trend,
        "weekly_labels": week_dates,
        "habit_stats": habit_stats,
        "heatmap": heatmap
    })
# =========================
# 📅 WEEKLY PAGE
# =========================
@habit_bp.route("/weekly")
@login_required
def weekly_page():
    return render_template("weekly.html")


# =========================
# 📅 WEEKLY API
# =========================
@habit_bp.route("/api/weekly")
@login_required
def weekly_api():
    user = session.get("user", {}).get("email")

    today = datetime.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    # Fetch only this week
    logs = list(mongo.db.logs.find({
        "user": user,
        "date": {
            "$gte": start.strftime("%Y-%m-%d"),
            "$lte": end.strftime("%Y-%m-%d")
        }
    }))

    # Initialize full week
    days = []
    log_map = {}

    for log in logs:
        log_map.setdefault(log["date"], 0)
        log_map[log["date"]] += 1

    for i in range(7):
        d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        count = log_map.get(d, 0)

        days.append({
            "date": d,
            "count": count
        })

    # 🔥 streak calculation
    streak = 0
    for day in reversed(days):
        if day["count"] > 0:
            streak += 1
        else:
            break

    # 📊 consistency
    active_days = sum(1 for d in days if d["count"] > 0)
    consistency = int((active_days / 7) * 100)

    return jsonify({
        "week_start": start.strftime("%Y-%m-%d"),
        "week_end": end.strftime("%Y-%m-%d"),
        "days": days,
        "streak": streak,
        "consistency": consistency

    })
def get_intensity(count, max_count):
    if max_count == 0:
        return 0

    ratio = count / max_count

    if ratio == 0: return 0
    elif ratio < 0.33: return 1
    elif ratio < 0.66: return 2
    else: return 3

# =========================
# 🧪 TEST
# =========================
@habit_bp.route("/test")
def test():
    return "WORKING ✅"