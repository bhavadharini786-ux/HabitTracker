from datetime import date, timedelta, datetime
from app.utils.db import mongo


# =========================
# 🔥 STREAK (IMPROVED)
# =========================
def calculate_streak(user):

    logs = list(mongo.db.logs.find({"user": user}))

    # Unique completed days
    log_dates = sorted({
        datetime.strptime(log["date"], "%Y-%m-%d").date()
        for log in logs if log.get("date")
    }, reverse=True)

    if not log_dates:
        return 0

    streak = 0
    today = date.today()

    # 👉 Allow streak from yesterday if today not completed
    start_day = today if today in log_dates else today - timedelta(days=1)

    for d in log_dates:
        if d == start_day - timedelta(days=streak):
            streak += 1
        else:
            break

    return streak


# =========================
# 📊 DASHBOARD DATA
# =========================
def get_dashboard_data(user):

    today = date.today().isoformat()

    habits = list(mongo.db.habits.find({"user": user}))

    logs_today = list(mongo.db.logs.find({
        "user": user,
        "date": today
    }))

    # =========================
    # ✅ UNIQUE COMPLETED HABITS
    # =========================
    completed_ids = list({
        str(log["habit_id"]) for log in logs_today
        if "habit_id" in log
    })

    today_done = len(completed_ids)
    total_habits = len(habits)

    # =========================
    # 🏆 SCORE
    # =========================
    score = f"{today_done}/{total_habits}" if total_habits else "0/0"

    # =========================
    # 📊 COMPLETION %
    # =========================
    completion_percent = round(
        (today_done / total_habits) * 100
    ) if total_habits else 0

    # =========================
    # 🔥 STREAK
    # =========================
    streak = calculate_streak(user)

    # =========================
    # 🧠 REMAINING
    # =========================
    remaining = max(0, total_habits - today_done)

    return {
        "habits": habits,
        "completed_ids": completed_ids,
        "today_count": today_done,
        "streak": streak,
        "score": score,
        "completion_percent": completion_percent,
        "remaining": remaining
    }