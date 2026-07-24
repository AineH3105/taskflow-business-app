import json

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

TASKS_FILE = "tasks.json"


def load_tasks():
    """Load tasks from the JSON file."""
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_tasks(tasks):
    """Save tasks to the JSON file."""
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


@app.route("/")
def home():
    all_tasks = load_tasks()

    total_tasks = len(all_tasks)
    completed_tasks = sum(
        1 for task in all_tasks if task["status"] == "Completed"
    )
    in_progress_tasks = sum(
        1 for task in all_tasks if task["status"] == "In Progress"
    )
    todo_tasks = sum(
        1 for task in all_tasks if task["status"] == "To Do"
    )

    selected_status = request.args.get("status", "All")
    search_query = request.args.get("search", "").strip()

    displayed_tasks = all_tasks

    if selected_status != "All":
        displayed_tasks = [
            task
            for task in displayed_tasks
            if task["status"] == selected_status
        ]

    if search_query:
        query = search_query.lower()

        displayed_tasks = [
            task
            for task in displayed_tasks
            if query in task["title"].lower()
            or query in task["assigned_to"].lower()
        ]

    return render_template(
        "index.html",
        tasks=displayed_tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        todo_tasks=todo_tasks,
        selected_status=selected_status,
        search_query=search_query,
    )


@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        tasks = load_tasks()

        new_task = {
            "id": max((task["id"] for task in tasks), default=0) + 1,
            "title": request.form["title"].strip(),
            "assigned_to": request.form["assigned_to"].strip(),
            "priority": request.form["priority"],
            "status": request.form["status"],
        }

        tasks.append(new_task)
        save_tasks(tasks)

        return redirect(url_for("home"))

    return render_template("add_task.html")


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    tasks = load_tasks()

    task = next(
        (task for task in tasks if task["id"] == task_id),
        None,
    )

    if task is None:
        return redirect(url_for("home"))

    if request.method == "POST":
        task["title"] = request.form["title"].strip()
        task["assigned_to"] = request.form["assigned_to"].strip()
        task["priority"] = request.form["priority"]
        task["status"] = request.form["status"]

        save_tasks(tasks)
        return redirect(url_for("home"))

    return render_template("edit_task.html", task=task)


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "Completed"
            break

    save_tasks(tasks)
    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    tasks = load_tasks()

    tasks = [
        task
        for task in tasks
        if task["id"] != task_id
    ]

    save_tasks(tasks)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)