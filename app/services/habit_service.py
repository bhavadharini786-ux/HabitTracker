from datetime import date
from app.repositories import log_repo, habit_repo


# =========================
# 🔁 TOGGLE HABIT LOGIC
# =========================
def toggle_habit(user, habit_id):

    # 1. Validate habit
    habit = habit_repo.get_habit_by_id(habit_id)

    if not habit:
        return {"error": "Habit not found"}, 404

    # 2. Ownership check
    if habit.get("user") != user:
        return {"error": "Unauthorized"}, 403

    today = date.today().isoformat()

    # 3. Toggle log
    try:
        toggled = log_repo.toggle_log(user, habit_id, today)
    except Exception as e:
        return {"error": "Toggle failed", "details": str(e)}, 500

    # 4. Response
    return {
        "success": True,
        "status": "completed" if toggled else "removed"
    }
