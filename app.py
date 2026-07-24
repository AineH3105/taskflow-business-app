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
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)


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


if __name__ == "__main__":
    app.run(debug=True)