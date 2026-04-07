import csv
import logging
import os

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import (LoginManager, current_user, login_required, login_user,
                         logout_user)

from config import Config
from models import AccessLog, Guard, Student, db
from nlp_utils import extract_prn, validate_prn


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["LOG_FOLDER"], exist_ok=True)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

logger = logging.getLogger("access_logger")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(os.path.join(app.config["LOG_FOLDER"], "access.log"))
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


@login_manager.user_loader
def load_user(user_id):
    return Guard.query.get(int(user_id))


@app.before_request
def bootstrap_data():
    db.create_all()
    if not Guard.query.filter_by(username="guard").first():
        db.session.add(Guard(username="guard", password="guard123"))
        db.session.commit()


@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        guard = Guard.query.filter_by(username=username, password=password).first()
        if guard:
            login_user(guard)
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        text_input = request.form.get("prn_text", "")
        prn = extract_prn(text_input)
        if not prn or not validate_prn(prn):
            result = "Invalid PRN format"
            save_log(prn or "N/A", result)
            flash("Could not find a valid PRN in input.", "warning")
            return render_template("verify_result.html", student=None, prn=prn, result=result)

        student = Student.query.get(prn)
        if student:
            result = f"Verified - {student.status}"
            save_log(prn, result)
            return render_template("verify_result.html", student=student, prn=prn, result=result)

        result = "Student not found"
        save_log(prn, result)
        flash("No student found for this PRN.", "danger")
        return render_template("verify_result.html", student=None, prn=prn, result=result)

    recent_logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(10).all()
    return render_template("dashboard.html", recent_logs=recent_logs)


def save_log(prn, result):
    entry = AccessLog(prn=prn, guard=current_user.username, result=result)
    db.session.add(entry)
    db.session.commit()
    logger.info("guard=%s prn=%s result=%s", current_user.username, prn, result)


@app.route("/students")
@login_required
def student_list():
    query = request.args.get("q", "").strip()
    students_qs = Student.query
    if query:
        students_qs = students_qs.filter(Student.prn.contains(query))
    students = students_qs.order_by(Student.prn.asc()).all()
    return render_template("student_list.html", students=students, query=query)


@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        form = request.form
        prn = form.get("prn", "").strip()

        if not validate_prn(prn):
            flash("PRN must be 8 to 12 digits.", "danger")
            return render_template("add_student.html", student=None)

        if Student.query.get(prn):
            flash("Duplicate PRN not allowed.", "danger")
            return render_template("add_student.html", student=None)

        student = Student(
            prn=prn,
            name=form.get("name", "").strip(),
            branch=form.get("branch", "").strip(),
            year=form.get("year", "").strip(),
            section=form.get("section", "").strip(),
            email=form.get("email", "").strip(),
            phone=form.get("phone", "").strip(),
            photo_url=form.get("photo_url", "").strip(),
            status=form.get("status", "active").strip().lower(),
        )

        if not student.name or not student.branch or not student.year:
            flash("Name, branch and year are required.", "danger")
            return render_template("add_student.html", student=None)

        db.session.add(student)
        db.session.commit()
        flash("Student added successfully.", "success")
        return redirect(url_for("student_list"))

    return render_template("add_student.html", student=None)


@app.route("/students/edit/<prn>", methods=["GET", "POST"])
@login_required
def edit_student(prn):
    student = Student.query.get_or_404(prn)

    if request.method == "POST":
        form = request.form
        student.name = form.get("name", "").strip()
        student.branch = form.get("branch", "").strip()
        student.year = form.get("year", "").strip()
        student.section = form.get("section", "").strip()
        student.email = form.get("email", "").strip()
        student.phone = form.get("phone", "").strip()
        student.photo_url = form.get("photo_url", "").strip()
        student.status = form.get("status", "active").strip().lower()

        if not student.name or not student.branch or not student.year:
            flash("Name, branch and year are required.", "danger")
            return render_template("add_student.html", student=student)

        db.session.commit()
        flash("Student updated successfully.", "success")
        return redirect(url_for("student_list"))

    return render_template("add_student.html", student=student)


@app.route("/students/delete/<prn>", methods=["POST"])
@login_required
def delete_student(prn):
    student = Student.query.get_or_404(prn)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted.", "info")
    return redirect(url_for("student_list"))


CHATBOT_KNOWLEDGE = {
    "what is artificial intelligence": "Artificial Intelligence is a technology that enables machines to simulate human intelligence and perform tasks such as learning, reasoning, and decision-making.",
    "what is machine learning": "Machine Learning is a branch of AI where systems learn patterns from data and improve performance without being explicitly programmed for every rule.",
    "what is nlp": "Natural Language Processing (NLP) helps computers understand and generate human language in text or speech form.",
    "what is python": "Python is a high-level programming language known for readability and strong support for web development, AI, and automation.",
    "what is flask": "Flask is a lightweight Python web framework used to build web applications and APIs quickly.",
}


def generate_chatbot_response(message, history=None):
    history = history or []
    normalized = " ".join((message or "").strip().lower().split())

    if not normalized:
        return "Please type a message so I can help you."

    if normalized in CHATBOT_KNOWLEDGE:
        return CHATBOT_KNOWLEDGE[normalized]

    greetings = {"hi", "hello", "hey", "good morning", "good evening"}
    if normalized in greetings:
        return "Hello! Ask me anything about AI, machine learning, NLP, Python, or Flask."

    if "your name" in normalized:
        return "I am Practical-5 Chatbot, built to provide intelligent responses to your queries."

    if "help" in normalized:
        return "You can ask questions like: What is Artificial Intelligence?, What is NLP?, or What is Flask?"

    if history:
        return "I understand your question. I am still learning, but I can explain AI, NLP, machine learning, Python, and Flask right now."

    return "I am not fully trained for that yet. Please ask about AI, machine learning, NLP, Python, or Flask."


@app.route("/chatbot")
@login_required
def chatbot_view():
    return render_template("chatbot.html")


@app.route("/api/chatbot", methods=["POST"])
@login_required
def chatbot_api():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", ""))
    history = payload.get("history", [])
    if not isinstance(history, list):
        history = []

    reply = generate_chatbot_response(message, history)
    return jsonify({"reply": reply})


EXPECTED_HEADER = ["prn", "name", "branch", "year", "section", "email", "phone", "photo_url", "status"]


@app.route("/import", methods=["GET", "POST"])
@login_required
def import_students_view():
    if request.method == "POST":
        file = request.files.get("csv_file")
        if not file or not file.filename.endswith(".csv"):
            flash("Please upload a valid CSV file.", "danger")
            return render_template("import.html", errors=[])

        save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(save_path)

        inserted, errors = import_from_csv(save_path)
        if inserted:
            flash(f"Imported {inserted} students.", "success")
        if errors:
            flash(f"Import completed with {len(errors)} error(s).", "warning")
        return render_template("import.html", errors=errors)

    return render_template("import.html", errors=[])


def import_from_csv(path):
    inserted = 0
    errors = []
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames != EXPECTED_HEADER:
            return 0, [
                "Invalid CSV header. Expected: prn,name,branch,year,section,email,phone,photo_url,status"
            ]

        for row_number, row in enumerate(reader, start=2):
            prn = row["prn"].strip()
            if not validate_prn(prn):
                errors.append(f"Row {row_number}: invalid PRN")
                continue
            if Student.query.get(prn):
                errors.append(f"Row {row_number}: duplicate PRN {prn}")
                continue
            if not row["name"].strip() or not row["branch"].strip() or not row["year"].strip():
                errors.append(f"Row {row_number}: missing required fields")
                continue

            student = Student(
                prn=prn,
                name=row["name"].strip(),
                branch=row["branch"].strip(),
                year=row["year"].strip(),
                section=row["section"].strip(),
                email=row["email"].strip(),
                phone=row["phone"].strip(),
                photo_url=row["photo_url"].strip(),
                status=row["status"].strip().lower() or "active",
            )
            db.session.add(student)
            inserted += 1

        db.session.commit()
    return inserted, errors


if __name__ == "__main__":
    app.run(debug=True)
