from datetime import datetime
from app.utils.db import mongo
from bson import ObjectId


def get_analytics(user):
    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"user": user}))

    total_habits = len(habits)
    total_logs = len(logs)

    # ------------------ 📊 Completion Rate ------------------
    unique_days = len(set(log["date"] for log in logs))

    completion_rate = int(
        (total_logs / (total_habits * unique_days)) * 100
    ) if total_habits and unique_days else 0

    # ------------------ 🔥 Best Streak ------------------
    best_streak = 0
    current_streak = 0

    # Sort logs by date
    sorted_logs = sorted(logs, key=lambda x: x["date"])

    prev_date = None

    for log in sorted_logs:
        current_date = datetime.strptime(log["date"], "%Y-%m-%d")

        if prev_date:
            diff = (current_date - prev_date).days

            if diff == 1:
                current_streak += 1
            else:
                current_streak = 1
        else:
            current_streak = 1

        best_streak = max(best_streak, current_streak)
        prev_date = current_date

    # ------------------ 🏆 Top Habit ------------------
    habit_count = {}

    for log in logs:
        habit_id = str(log["habit_id"])
        habit_count[habit_id] = habit_count.get(habit_id, 0) + 1

    top_habit = None

    if habit_count:
        top_id = max(habit_count, key=habit_count.get)

        habit = mongo.db.habits.find_one({"_id": ObjectId(top_id)})
        if habit:
            top_habit = habit["name"]

    # ------------------ ❌ Missed Days ------------------
    days_with_logs = len(set(log["date"] for log in logs))
    missed_days = max(0, 7 - days_with_logs)

    # ------------------ 📈 Weekly Trend ------------------
    week_data = [0, 0, 0, 0, 0, 0, 0]  # Mon → Sun

    for log in logs:
        d = datetime.strptime(log["date"], "%Y-%m-%d")
        week_data[d.weekday()] += 1

    return {
        "completion_rate": completion_rate,
        "best_streak": best_streak,
        "top_habit": top_habit,
        "missed_days": missed_days,
        "weekly_trend": week_data
    }