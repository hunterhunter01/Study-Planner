"""
Study Planner — Main Flask Application
========================================
Entry point: route handlers, authentication, task management,
database session handling, and the automatic scheduling engine.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, get_db_connection
from datetime import datetime, timedelta
import hashlib
import os

app = Flask(__name__)
# Change this to a long random string in production (e.g. secrets.token_hex(32))
app.secret_key = os.environ.get("SECRET_KEY", "studyplanner-dev-secret-2024")

# Premium access code — change this to whatever code you want users to enter
PREMIUM_CODE = os.environ.get("PREMIUM_CODE", "0000")


# ──────────────────────────────────────────────────────────
# UTILITY: Password hashing
# We use SHA-256 for simplicity. In production, use bcrypt.
# ──────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ──────────────────────────────────────────────────────────
# SCHEDULING ENGINE
# Called every time the dashboard loads.
# Reads incomplete tasks → sorts by priority + deadline →
# assigns sequential study blocks → writes to schedules table.
# ──────────────────────────────────────────────────────────

# Maps priority label to a numeric sort key (lower = sooner)
PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}

# Estimated study minutes per task type
TASK_DURATIONS = {"Assignment": 90, "Quiz": 45, "Exam": 120, "Other": 60}

# Break between scheduled blocks (minutes)
BREAK_MINUTES = 15


def generate_schedule(user_id: int) -> list:
    """
    Automatic Schedule Generation Engine.

    Steps:
      1. Fetch all 'Pending' / 'In Progress' tasks for the user.
      2. Sort by (priority_rank ASC, deadline ASC) — highest priority
         tasks with the earliest deadlines are scheduled first.
      3. Assign back-to-back study slots starting from right now,
         with a short break between each block.
      4. Upsert results into the schedules table.
      5. Return the enriched list so the dashboard can render it.
    """
    conn   = get_db_connection()
    cursor = conn.cursor()

    # Pull incomplete tasks for this user
    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND status != 'Completed'",
        (user_id,)
    )
    tasks = cursor.fetchall()

    if not tasks:
        conn.close()
        return []

    # --- Sort: primary = priority rank, secondary = deadline (ascending) ---
    def sort_key(task):
        rank = PRIORITY_ORDER.get(task["priority"], 99)
        try:
            dl = datetime.strptime(task["deadline"], "%Y-%m-%dT%H:%M")
        except ValueError:
            try:
                dl = datetime.strptime(task["deadline"], "%Y-%m-%d %H:%M")
            except ValueError:
                dl = datetime.max
        return (rank, dl)

    sorted_tasks = sorted(tasks, key=sort_key)

    # --- Assign sequential time slots starting from now ---
    slot_start = datetime.now().replace(second=0, microsecond=0)
    scheduled  = []

    for task in sorted_tasks:
        duration  = TASK_DURATIONS.get(task["task_type"], 60)
        slot_end  = slot_start + timedelta(minutes=duration)

        # Upsert: remove old schedule entry, insert fresh one
        cursor.execute("DELETE FROM schedules WHERE task_id = ?", (task["id"],))
        cursor.execute(
            "INSERT INTO schedules (user_id, task_id, scheduled_start, scheduled_end) "
            "VALUES (?, ?, ?, ?)",
            (
                user_id,
                task["id"],
                slot_start.strftime("%Y-%m-%d %H:%M"),
                slot_end.strftime("%Y-%m-%d %H:%M"),
            ),
        )

        # Build the dict the template will render
        scheduled.append({
            "task":            dict(task),
            "scheduled_start": slot_start.strftime("%b %d, %Y · %H:%M"),
            "scheduled_end":   slot_end.strftime("%H:%M"),
            "duration":        duration,
        })

        # Next block starts after this one + break
        slot_start = slot_end + timedelta(minutes=BREAK_MINUTES)

    conn.commit()
    conn.close()
    return scheduled


# ──────────────────────────────────────────────────────────
# NOTIFICATION HELPER
# Returns two lists: overdue tasks and tasks due within 24 h.
# ──────────────────────────────────────────────────────────
def get_notifications(user_id: int):
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND status != 'Completed'",
        (user_id,)
    )
    tasks = cursor.fetchall()
    conn.close()

    now      = datetime.now()
    overdue  = []
    due_soon = []

    for task in tasks:
        # Support both datetime-local format and stored format
        for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
            try:
                dl = datetime.strptime(task["deadline"], fmt)
                break
            except ValueError:
                dl = None

        if dl is None:
            continue

        if dl < now:
            overdue.append(dict(task))
        elif dl <= now + timedelta(hours=24):
            due_soon.append(dict(task))

    return overdue, due_soon


# ──────────────────────────────────────────────────────────
# ROUTES — Authentication
# ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Root redirect: dashboard if authenticated, else login."""
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    GET  → render registration form.
    POST → validate fields, hash password, insert user row.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        conn   = get_db_connection()
        cursor = conn.cursor()

        # Reject duplicate usernames / emails
        cursor.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        )
        if cursor.fetchone():
            conn.close()
            flash("Username or email is already registered.", "danger")
            return redirect(url_for("register"))

        # Insert new user — password stored as SHA-256 hash, never plaintext
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, hash_password(password)),
        )
        conn.commit()
        conn.close()

        flash("Account created — please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  → render login form.
    POST → verify credentials, write user_id + username to session.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, hash_password(password)),
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            # Write to server-side session (stored in signed cookie)
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ──────────────────────────────────────────────────────────
# ROUTES — Dashboard
# ──────────────────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    """
    Main interface.
    1. Guard: redirect to login if not authenticated.
    2. Run scheduling engine → get ordered study slots.
    3. Run notification helper → overdue + due-soon lists.
    4. Render dashboard template with all data.
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id         = session["user_id"]
    schedule        = generate_schedule(user_id)
    overdue, due_soon = get_notifications(user_id)

    return render_template(
        "dashboard.html",
        schedule=schedule,
        overdue=overdue,
        due_soon=due_soon,
        username=session["username"],
    )


# ──────────────────────────────────────────────────────────
# ROUTES — Task Management
# ──────────────────────────────────────────────────────────

@app.route("/add_task", methods=["POST"])
def add_task():
    """
    Receives POST data from the 'Add Task' form on the dashboard.

    Data flow:
      HTML form (dashboard.html)
        → POST /add_task
          → validated + inserted into tasks table
            → redirect to /dashboard (scheduler re-runs automatically)

    Form fields:
      task_name  — free text
      task_type  — Assignment | Quiz | Exam | Other
      deadline   — datetime-local  (browsers send YYYY-MM-DDTHH:MM)
      priority   — High | Medium | Low
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    task_name = request.form.get("task_name", "").strip()
    task_type = request.form.get("task_type", "Other")
    deadline  = request.form.get("deadline",  "")
    priority  = request.form.get("priority",  "Medium")

    if not task_name or not deadline:
        flash("Task name and deadline are required.", "danger")
        return redirect(url_for("dashboard"))

    conn   = get_db_connection()
    cursor = conn.cursor()

    # Insert task linked to the current session's user
    cursor.execute(
        "INSERT INTO tasks (user_id, task_name, task_type, deadline, priority, status) "
        "VALUES (?, ?, ?, ?, ?, 'Pending')",
        (session["user_id"], task_name, task_type, deadline, priority),
    )
    conn.commit()
    conn.close()

    flash(f'Task "{task_name}" added!', "success")
    return redirect(url_for("dashboard"))


@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id: int):
    """Mark a task as Completed (removes it from the schedule on next load)."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn   = get_db_connection()
    cursor = conn.cursor()
    # Scope update to the logged-in user to prevent cross-user manipulation
    cursor.execute(
        "UPDATE tasks SET status = 'Completed' WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"]),
    )
    conn.commit()
    conn.close()

    flash("Task marked as completed ✓", "success")
    return redirect(url_for("dashboard"))


@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id: int):
    """Permanently delete a task and its schedule entry."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tasks     WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"]),
    )
    cursor.execute("DELETE FROM schedules WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()

    flash("Task deleted.", "info")
    return redirect(url_for("dashboard"))


# ──────────────────────────────────────────────────────────
# ROUTES — Premium Features
# ──────────────────────────────────────────────────────────

@app.route("/analytics")
def analytics():
    """Premium: Analytics dashboard with task statistics."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    if not session.get("is_premium"):
        flash("This is a Premium feature. Enter your code to unlock it.", "warning")
        return redirect(url_for("premium"))

    user_id = session["user_id"]
    conn    = get_db_connection()
    cursor  = conn.cursor()

    # All tasks for this user
    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    all_tasks = [dict(r) for r in cursor.fetchall()]
    conn.close()

    completed  = [t for t in all_tasks if t["status"] == "Completed"]
    pending    = [t for t in all_tasks if t["status"] != "Completed"]

    # By type
    type_counts = {}
    for t in all_tasks:
        type_counts[t["task_type"]] = type_counts.get(t["task_type"], 0) + 1

    # By priority
    priority_counts = {}
    for t in all_tasks:
        priority_counts[t["priority"]] = priority_counts.get(t["priority"], 0) + 1

    # Completion rate
    total = len(all_tasks)
    completion_rate = round(len(completed) / total * 100) if total else 0

    # Study hours scheduled (pending tasks only)
    TASK_DURATIONS = {"Assignment": 90, "Quiz": 45, "Exam": 120, "Other": 60}
    total_minutes = sum(TASK_DURATIONS.get(t["task_type"], 60) for t in pending)

    return render_template(
        "analytics.html",
        all_tasks=all_tasks,
        completed=completed,
        pending=pending,
        type_counts=type_counts,
        priority_counts=priority_counts,
        completion_rate=completion_rate,
        total_minutes=total_minutes,
        username=session["username"],
    )


@app.route("/calendar")
def calendar_view():
    """Premium: Calendar view of scheduled tasks."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    if not session.get("is_premium"):
        flash("This is a Premium feature. Enter your code to unlock it.", "warning")
        return redirect(url_for("premium"))

    user_id  = session["user_id"]
    schedule = generate_schedule(user_id)

    # Build a JSON-serialisable list for FullCalendar
    events = []
    TASK_COLORS = {"Assignment": "#4f46e5", "Quiz": "#7c3aed", "Exam": "#dc2626", "Other": "#0891b2"}
    for item in schedule:
        task = item["task"]
        # Parse slot start/end back to ISO
        try:
            s = datetime.strptime(item["scheduled_start"], "%b %d, %Y · %H:%M")
            e_str = item["scheduled_start"].split("·")[0].strip() + " · " + item["scheduled_end"]
            e = datetime.strptime(
                item["scheduled_start"].split("·")[0].strip().strip() + " " + item["scheduled_end"],
                "%b %d, %Y  %H:%M"
            )
        except Exception:
            continue

        events.append({
            "id":    task["id"],
            "title": task["task_name"],
            "start": s.strftime("%Y-%m-%dT%H:%M:00"),
            "end":   e.strftime("%Y-%m-%dT%H:%M:00"),
            "color": TASK_COLORS.get(task["task_type"], "#64748b"),
            "extendedProps": {
                "type":     task["task_type"],
                "priority": task["priority"],
                "deadline": task["deadline"],
                "status":   task["status"],
            }
        })

    import json
    return render_template(
        "calendar.html",
        events_json=json.dumps(events),
        username=session["username"],
    )


@app.route("/ai_recommendations")
def ai_recommendations():
    """Premium: AI-powered study recommendations."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    if not session.get("is_premium"):
        flash("This is a Premium feature. Enter your code to unlock it.", "warning")
        return redirect(url_for("premium"))

    user_id = session["user_id"]
    conn    = get_db_connection()
    cursor  = conn.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND status != 'Completed'",
        (user_id,)
    )
    pending_tasks = [dict(r) for r in cursor.fetchall()]
    conn.close()

    overdue, due_soon = get_notifications(user_id)

    return render_template(
        "ai_recommendations.html",
        pending_tasks=pending_tasks,
        overdue=overdue,
        due_soon=due_soon,
        username=session["username"],
    )


# ──────────────────────────────────────────────────────────
# ROUTES — Premium Activation
# ──────────────────────────────────────────────────────────

@app.route("/premium")
def premium():
    """Show the premium code entry page."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("premium.html")


@app.route("/activate_premium", methods=["POST"])
def activate_premium():
    """Validate the entered premium code and unlock premium features."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    code = request.form.get("code", "").strip()
    if code == PREMIUM_CODE:
        session["is_premium"] = True
        flash("Premium features unlocked! Enjoy Analytics, Calendar, and AI Coach.", "success")
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid premium code. Please try again.", "danger")
        return redirect(url_for("premium"))


# ──────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()          # Create tables + seed mock data on first run
    app.run(debug=True, port=5000)
