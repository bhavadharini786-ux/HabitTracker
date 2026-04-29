from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify
from app.utils.db import mongo
from bson import ObjectId
from datetime import datetime, date, timedelta
from app.utils.auth import api_login_required, login_required
habit_bp = Blueprint("habit", __name__)

# ------------------ HOME ------------------
@habit_bp.route("/home")
@api_login_required
def home():
    return render_template("dashboard.html")


# ------------------ CREATE HABIT ------------------
@habit_bp.route("/create", methods=["POST"])
@api_login_required
def create_habit():
    mongo.db.habits.insert_one({
        "name": request.form["name"],
        "time": request.form["time"],
        "user": session.get("user"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    return redirect(url_for("habit.dashboard"))


# ------------------ VIEW HABITS ------------------
@habit_bp.route("/habits")
@api_login_required
def habits():
    user = session.get("user")
    habits = list(mongo.db.habits.find({"user": user}))
    return render_template("habits.html", habits=habits)


# ------------------ DELETE ------------------
@habit_bp.route("/delete/<id>")
@api_login_required
def delete_habit(id):
    user = session.get("user")

    habit = mongo.db.habits.find_one({"_id": ObjectId(id)})

    if not habit or habit["user"] != user:
        return "Unauthorized", 403

    mongo.db.habits.delete_one({"_id": ObjectId(id)})
    mongo.db.logs.delete_many({"habit_id": id})

    return redirect(url_for("habit.dashboard"))

# ------------------ EDIT ------------------
@habit_bp.route("/edit/<id>", methods=["GET", "POST"])
@api_login_required
def edit_habit(id):
    user = session.get("user")

    habit = mongo.db.habits.find_one({"_id": ObjectId(id)})

    # 🔐 ownership check
    if not habit or habit["user"] != user:
        return "Unauthorized", 403

    if request.method == "POST":
        mongo.db.habits.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": request.form["name"],
                "time": request.form["time"]
            }}
        )
        return redirect(url_for("habit.dashboard"))

    return render_template("edit_habit.html", habit=habit)


# ------------------ TOGGLE ------------------
@habit_bp.route("/toggle/<habit_id>")
@api_login_required
def toggle_habit(habit_id):
    user = session.get("user")

    habit = mongo.db.habits.find_one({"_id": ObjectId(habit_id)})

    if not habit or habit["user"] != user:
        return "Unauthorized", 403

    today = str(date.today())

    existing = mongo.db.logs.find_one({
        "habit_id": habit_id,
        "date": today,
        "user": user
    })

    if existing:
        mongo.db.logs.delete_one({"_id": existing["_id"]})
    else:
        mongo.db.logs.insert_one({
            "habit_id": habit_id,
            "date": today,
            "completed": True,
            "user": user
        })

    return redirect(url_for("habit.dashboard"))

# ------------------ STREAK FUNCTION ------------------
def calculate_streak(user):
    streak = 0

    for i in range(365):
        day = str(date.today() - timedelta(days=i))

        log_exists = mongo.db.logs.find_one({
            "user": user,
            "date": day
        })

        if log_exists:
            streak += 1
        else:
            break

    return streak
# ------------------ DASHBOARD ------------------

@habit_bp.route("/dashboard")
@api_login_required
def dashboard():
    user = session.get("user")
    today = str(date.today())

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"date": today, "user": user}))

    completed_ids = [log["habit_id"] for log in logs]

    today_count = len(completed_ids)
    streak = calculate_streak(user)

    total_habits = len(habits)
    today_done = len(completed_ids)

    score = f"{today_done}/{total_habits}" if total_habits else "0/0"
    completion_percent = int((today_done / total_habits) * 100) if total_habits else 0

    return render_template(
        "dashboard.html",
        habits=habits,
        completed_ids=completed_ids,
        today_count=today_count,
        streak=streak,
        score=score,
        completion_percent=completion_percent
    )

# ------------------ WEEKLY PAGE ------------------
@habit_bp.route("/weekly-page")
@api_login_required
def weekly_page():
    return render_template("weekly.html")
# ------------------ ANALYTICS PAGE ------------------
@habit_bp.route("/analytics")
@api_login_required
def analytics_page():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("analytics.html")


# ------------------ WEEKLY API ------------------
@habit_bp.route("/api/weekly")
@api_login_required
def get_weekly_data():
    user = session.get("user")

    today = datetime.today()
    start = today - timedelta(days=today.weekday())

    week_data = {d: 0 for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]}

    logs = mongo.db.logs.find({"user": user})

    for log in logs:
        log_date = datetime.strptime(log["date"], "%Y-%m-%d")
        if start.date() <= log_date.date() <= (start + timedelta(days=6)).date():
            day = log_date.strftime("%a")
            week_data[day] += 1

    return jsonify({"data": week_data})


# ------------------ DAY DETAILS ------------------
@habit_bp.route("/api/day/<date>")
@api_login_required
def day_details(date):
    logs = list(mongo.db.logs.find({"date": date}))

    habits = []
    for log in logs:
        habit = mongo.db.habits.find_one({"_id": ObjectId(log["habit_id"])})
        if habit:
            habits.append({
                "name": habit["name"],
                "habit_id": str(habit["_id"])
            })

    return jsonify({"date": date, "habits": habits})


# ------------------ # ------------------ ANALYTICS API ------------------
@habit_bp.route("/api/analytics")
@api_login_required
def analytics_api():
    

    user = session.get("user")

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"user": user}))

    total_habits = len(habits)
    total_logs = len(logs)

    # 📊 Completion Rate
    completion_rate = int((total_logs / (total_habits * 7)) * 100) if total_habits else 0

    # 🔥 Best streak (simple)
    best_streak = 0
    current = 0

    sorted_logs = sorted(logs, key=lambda x: x["date"])

    prev_date = None
    for log in sorted_logs:
        d = log["date"]

        if prev_date:
            diff = (datetime.strptime(d, "%Y-%m-%d") - datetime.strptime(prev_date, "%Y-%m-%d")).days
            if diff == 1:
                current += 1
            else:
                current = 1
        else:
            current = 1

        best_streak = max(best_streak, current)
        prev_date = d

    # 🏆 Top Habit
    habit_count = {}
    for log in logs:
        habit_count[log["habit_id"]] = habit_count.get(log["habit_id"], 0) + 1

    top_habit = None
    if habit_count:
        top_id = max(habit_count, key=habit_count.get)
        habit = mongo.db.habits.find_one({"_id": ObjectId(top_id)})
        if habit:
            top_habit = habit["name"]

    # ❌ Missed days
    missed_days = max(0, 7 - (total_logs // total_habits)) if total_habits else 0

    # 📈 Weekly trend
    week_data = [0,0,0,0,0,0,0]

    for log in logs:
        d = datetime.strptime(log["date"], "%Y-%m-%d")
        week_data[d.weekday()] += 1

    return jsonify({
        "completion_rate": completion_rate,
        "best_streak": best_streak,
        "top_habit": top_habit,
        "missed_days": missed_days,
        "weekly_trend": week_data
    })
@habit_bp.route("/api/heatmap")
@api_login_required
def heatmap():
    user = session.get("user")

    logs = list(mongo.db.logs.find({"user": user}))

    data = {}

    for log in logs:
        date = log["date"]
        data[date] = data.get(date, 0) + 1

    return jsonify(data)
