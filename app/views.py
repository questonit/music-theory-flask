from flask import current_app, Blueprint, render_template, request
from flask_login import current_user, login_required
from app.models import Test, User

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

    for test in Test.objects(teacher_id=current_user.user_id):
        tests.append((test.test_id, test.name))

    return render_template("views/teacher_tests.html", tests=tests)


@views.route("/tests/test")
@login_required
def test():
    test_id = request.args.get("id")
    test = Test.objects(test_id=test_id).first()

    return render_template("views/test.html", test=test)


@views.route("/student_statistics")
@login_required
def student_statistics():
    if current_user.role != "student":
        return render_template("views/forbid.html", title="Ошибка"), 403

    results = []

    return render_template("views/student_statistics.html", results=results)
