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

    user = session.get("user")
    today = str(date.today())

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({
        "user": user,
        "date": today
    }))

    completed_ids = [str(log["habit_id"]) for log in logs]

    return render_template(
        "dashboard.html",
        habits=habits,
        completed_ids=completed_ids,
        today=today
    )


# =========================
# 📊 DASHBOARD API
# =========================
@habit_bp.route("/api/dashboard")
@login_required
def dashboard_api():

    user = session.get("user")
    today = str(date.today())

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({
        "user": user,
        "date": today
    }))

    return jsonify({
        "total": len(habits),
        "completed": len(logs)
    })


# =========================
# ➕ CREATE HABIT
# =========================

@habit_bp.route("/create", methods=["POST"])
@login_required
def create_habit():

    user = session.get("user")

    mongo.db.habits.insert_one({
        "name": request.form["name"],
        "time": request.form["time"],
        "user": user,
        "created_at": datetime.utcnow()
    })

    return redirect(url_for("habit.dashboard"))
  


# =========================
# 📋 HABITS PAGE
# =========================
@habit_bp.route("/habits")
@login_required
def habits():

    user = session.get("user")
    today = str(date.today())

    habits = list(mongo.db.habits.find({"user": user}))

    logs = list(mongo.db.logs.find({
        "user": user,
        "date": today
    }))

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

    user = session.get("user")
    today = str(date.today())

    try:
        oid = ObjectId(habit_id)
    except:
        return "Invalid habit id", 400

    habit = mongo.db.habits.find_one({
        "_id": oid,
        "user": user
    })

    if not habit:
        return "Habit not found", 404

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

    user = session.get("user")

    try:
        oid = ObjectId(id)
    except:
        return "Invalid id", 400

    habit = mongo.db.habits.find_one({
        "_id": oid,
        "user": user
    })

    if not habit:
        return "Habit not found", 404

    mongo.db.habits.delete_one({"_id": oid})
    mongo.db.logs.delete_many({"habit_id": oid})

    return redirect(url_for("habit.habits"))


# =========================
# ✏️ EDIT HABIT
# =========================

# =========================
# ✏️ EDIT HABIT
# =========================
@habit_bp.route("/edit_habit/<habit_id>", methods=["GET", "POST"])
@login_required
def edit_habit(habit_id):

    user = session.get("user")

    try:
        oid = ObjectId(habit_id)
    except:
        return "Invalid habit id", 400

    # Find habit
    habit = mongo.db.habits.find_one({
        "_id": oid,
        "user": user
    })

    if not habit:
        return "Habit not found", 404

    # Update habit
    if request.method == "POST":

        mongo.db.habits.update_one(
            {"_id": oid},
            {
                "$set": {
                    "name": request.form.get("name"),
                    "time": request.form.get("time")
                }
            }
        )

        return redirect(url_for("habit.habits"))

    return render_template(
        "edit_habit.html",
        habit=habit
    )

# =========================
# 📊 ANALYTICS PAGE
# =========================
@habit_bp.route("/analytics")
@login_required
def analytics_page():
    return render_template("analytics.html")


# =========================
# 📊 ANALYTICS API
# =========================
# =========================
# 📊 ANALYTICS API
# =========================
# =========================
# 📊 ANALYTICS API
# =========================
@habit_bp.route("/api/analytics")
@login_required
def analytics_api():

    user = session.get("user")

    habits = list(mongo.db.habits.find({
        "user": user
    }))

    logs = list(mongo.db.logs.find({
        "user": user
    }))

    total_habits = len(habits)

    # =========================
    # NO HABITS
    # =========================

    if total_habits == 0:
        return jsonify({
            "completion_rate": 0,
            "streak": 0,
            "top_habit": None,
            "weekly_trend": [],
            "weekly_labels": [],
            "habit_performance": [],
            "last_30_days": [],
            "missed_days": 0
        })

    # =========================
    # LOG MAP
    # =========================

    logs_map = {}

    for log in logs:

        d = log["date"]

        logs_map.setdefault(d, 0)
        logs_map[d] += 1

    today = datetime.today()

    # =========================
    # WEEKLY TREND
    # =========================

    start_week = today - timedelta(days=6)

    week_dates = [
        (start_week + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(7)
    ]

    weekly_trend = [
        logs_map.get(d, 0)
        for d in week_dates
    ]

    # =========================
    # COMPLETION RATE
    # =========================

    total_completed = sum(weekly_trend)

    total_possible = total_habits * 7

    completion_rate = 0

    if total_possible > 0:
        completion_rate = int(
            (total_completed / total_possible) * 100
        )

    # =========================
    # STREAK
    # =========================

    streak = 0

    for i in range(365):

        d = (
            today - timedelta(days=i)
        ).strftime("%Y-%m-%d")

        if logs_map.get(d, 0) > 0:
            streak += 1
        else:
            break

    # =========================
    # TOP HABIT
    # =========================

    habit_counts = {}

    for log in logs:

        hid = str(log["habit_id"])

        habit_counts[hid] = (
            habit_counts.get(hid, 0) + 1
        )

    top_habit = None
    max_count = 0

    for habit in habits:

        hid = str(habit["_id"])

        count = habit_counts.get(hid, 0)

        if count > max_count:
            max_count = count
            top_habit = habit["name"]

    # =========================
    # HABIT PERFORMANCE
    # =========================

    habit_performance = []

    for habit in habits:

        hid = str(habit["_id"])

        habit_performance.append({
            "name": habit["name"],
            "count": habit_counts.get(hid, 0)
        })

    # =========================
    # LAST 30 DAYS HEATMAP
    # =========================

    last_30_days = []

    missed_days = 0

    for i in range(29, -1, -1):

        d = (
            today - timedelta(days=i)
        ).strftime("%Y-%m-%d")

        count = logs_map.get(d, 0)

        if count == 0:
            missed_days += 1

        last_30_days.append({
            "date": d,
            "count": count
        })

    # =========================
    # FINAL RESPONSE
    # =========================

    return jsonify({

        "completion_rate": completion_rate,

        "streak": streak,

        "top_habit": top_habit,

        "weekly_trend": weekly_trend,

        "weekly_labels": week_dates,

        "habit_performance": habit_performance,

        "last_30_days": last_30_days,

        "missed_days": missed_days
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
# =========================
# 📅 WEEKLY API
# =========================
@habit_bp.route("/api/weekly")
@login_required
def weekly_api():

    user = session.get("user")

    today = datetime.today()

    # Week start/end
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    # Get habits
    habits = list(
        mongo.db.habits.find({"user": user})
    )

    total_habits = len(habits)

    # Get logs
    logs = list(mongo.db.logs.find({
        "user": user,
        "date": {
            "$gte": start.strftime("%Y-%m-%d"),
            "$lte": end.strftime("%Y-%m-%d")
        }
    }))

    # Daily counts
    log_map = {}

    for log in logs:
        log_map.setdefault(log["date"], 0)
        log_map[log["date"]] += 1

    days = []

    for i in range(7):

        d = (
            start + timedelta(days=i)
        ).strftime("%Y-%m-%d")

        days.append({
            "date": d,
            "count": log_map.get(d, 0)
        })

    # =========================
    # 🔥 STREAK
    # =========================

    streak = 0

    for i in range(365):

        d = (
            today - timedelta(days=i)
        ).strftime("%Y-%m-%d")

        day_logs = mongo.db.logs.count_documents({
            "user": user,
            "date": d
        })

        if day_logs > 0:
            streak += 1
        else:
            break

    # =========================
    # 📈 CONSISTENCY
    # =========================

    total_completed = len(logs)

    total_possible = total_habits * 7

    consistency = 0

    if total_possible > 0:
        consistency = int(
            (total_completed / total_possible) * 100
        )

    return jsonify({
        "week_start": start.strftime("%Y-%m-%d"),
        "week_end": end.strftime("%Y-%m-%d"),
        "days": days,
        "streak": streak,
        "consistency": consistency
    })

# =========================
# 🧪 TEST ROUTE
# =========================
@habit_bp.route("/test")
def test():
    return "Habit routes working ✅"