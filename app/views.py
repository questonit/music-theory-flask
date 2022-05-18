import email
from turtle import title
from flask import current_app, Blueprint, render_template, request
from flask_login import current_user, login_required
from app.models import User

views = Blueprint("views", __name__, url_prefix="/")


@views.route("/")
def index():
    return render_template("views/index.html")


@views.route("/profile")
@login_required
def profile():

    return render_template(
        "views/profile.html", name=f"{current_user.first_name} {current_user.last_name}"
    )


@views.route("/users")
@login_required
def admin_users():
    if current_user.role != "admin":
        return render_template("views/forbid.html", title="Ошибка"), 403

    users = []
    number = 0

    for user in User.objects:
        number += 1
        users.append((number, user))

    return render_template("views/admin_users.html", users=users)


@views.route("/tests")
@login_required
def teacher_tests():
    if current_user.role != "teacher":
        return render_template("views/forbid.html", title="Ошибка"), 403

    tests = []

    return render_template("views/teacher_tests.html", tests=tests)


@views.route("/student_statistics")
@login_required
def student_statistics():
    if current_user.role != "student":
        return render_template("views/forbid.html", title="Ошибка"), 403

    results = []

    return render_template("views/student_statistics.html", results=results)
