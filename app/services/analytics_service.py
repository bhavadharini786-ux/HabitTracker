from datetime import datetime, timedelta
from app.utils.db import mongo
from bson import ObjectId


# =========================
# 📊 ANALYTICS ENGINE
# =========================
def get_analytics(user):

    habits = list(mongo.db.habits.find({"user": user}))
    logs = list(mongo.db.logs.find({"user": user}))

    total_habits = len(habits)

    # =========================
    # 📅 LAST 7 DAYS RANGE
    # =========================
    today = datetime.today()
    last_7_days = [
        (today - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(6, -1, -1)
    ]

    logs_last_7 = [log for log in logs if log["date"] in last_7_days]

    # =========================
    # 📊 COMPLETION RATE (FIXED)
    # =========================
    possible = total_habits * 7
    completion_rate = round((len(logs_last_7) / possible) * 100) if possible else 0

    # =========================
    # 🔥 BEST STREAK (STRICT DAILY)
    # =========================
    completed_days = sorted(set(
        datetime.strptime(log["date"], "%Y-%m-%d")
        for log in logs
    ))

    best_streak = 0
    current_streak = 0
    prev_date = None

    for d in completed_days:
        if prev_date and (d - prev_date).days == 1:
            current_streak += 1
        else:
            current_streak = 1

        best_streak = max(best_streak, current_streak)
        prev_date = d

    # =========================
    # 🏆 TOP HABIT
    # =========================
    habit_count = {}

    for log in logs_last_7:   # ✅ only recent
        hid = str(log["habit_id"])
        habit_count[hid] = habit_count.get(hid, 0) + 1

    top_habit = None

    if habit_count:
        top_id = max(habit_count, key=habit_count.get)

        habit = mongo.db.habits.find_one({"_id": ObjectId(top_id)})
        if habit:
            top_habit = habit.get("name")

    # =========================
    # ❌ MISSED DAYS (FIXED)
    # =========================
    completed_days_str = set(log["date"] for log in logs_last_7)
    missed_days = sum(1 for d in last_7_days if d not in completed_days_str)

    # =========================
    # 📈 WEEKLY TREND
    # =========================
    day_map = {d: 0 for d in last_7_days}

    for log in logs_last_7:
        day_map[log["date"]] += 1

    weekly_trend = list(day_map.values())

    # =========================
    # 📤 RESPONSE
    # =========================
    return {
        "completion_rate": completion_rate,
        "best_streak": best_streak,
        "top_habit": top_habit or "None",
        "missed_days": missed_days,
        "weekly_trend": weekly_trend
    }