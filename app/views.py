from flask import (
    current_app,
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from mongoengine.errors import NotUniqueError
from app.auth import check_email
from app.models import Result, Test, User, get_id

views = Blueprint("views", __name__, url_prefix="/")


@views.route("/")
def index():
    return render_template("views/index.html")


@views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_pass")
        last_password = request.form.get("last_pass")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        user = current_user

        if email and not check_email(email):
            flash("Неверный формат email")
            return redirect(url_for("views.profile"))

        if new_password and not user.check_password(last_password):
            flash("Неверный старый пароль")
            return redirect(url_for("views.profile"))

        if email:
            user.email = email

        if new_password:
            user.set_password(new_password)

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name
        try:
            user.save()
        except NotUniqueError:
            flash("Email уже используется")
            return redirect(url_for("views.profile"))

        flash("Данные успешно обновленны")

    return render_template("views/profile.html", title="Личный кабинет")


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

    return render_template("views/admin_users.html", users=users, title="Пользователи")


@views.route("/tests")
@login_required
def teacher_tests():
    if current_user.role != "teacher":
        return render_template("views/forbid.html", title="Ошибка"), 403

    tests = []

    for test in Test.objects(teacher_id=current_user.user_id):
        tests.append((test.test_id, test.name))

    return render_template("views/teacher_tests.html", tests=tests, title="Тесты")


@views.route("/tests/test")
@login_required
def test():
    if current_user.role != "teacher":
        return render_template("views/forbid.html", title="Ошибка"), 403

    test_id = request.args.get("id")
    test = Test.objects(test_id=test_id).first()

    return render_template(
        "views/test.html",
        test=test,
        count_questions=len(test.question_array),
        title=test.name,
    )


@views.route("/add_test", methods=["GET", "POST"])
@login_required
def add_test():
    if current_user.role != "teacher":
        return render_template("views/forbid.html", title="Ошибка"), 403

    if request.method == "POST":
        name = request.form.get("test_name")
        section = request.form.get("section")
        teacher_id = current_user.user_id
        test_id = get_id(Test.objects, "test_id")

        if not (name and section):
            flash("Не все поля заполнены!")
            return redirect(url_for("views.add_test"))

        new_test = Test(
            test_id=test_id,
            name=name,
            section=[section],
            question_array=[],
            teacher_id=teacher_id,
        )

        new_test.save()
        flash("Тест успешно создан!")
        return redirect(url_for("views.teacher_tests"))

    return render_template("views/add_test.html")


@views.route("/student_statistics")
@login_required
def student_statistics():
    if current_user.role != "student":
        return render_template("views/forbid.html", title="Ошибка"), 403

    results = []

    number = 0

    for result in Result.objects(user_id=current_user.user_id):
        number += 1
        test_name = Test.objects(test_id=result.test_id).first().name
        t_count = result.total_count
        i_count = result.incorrect_count
        mark = max(2, round((t_count - i_count) / t_count * 5))
        results.append((number, test_name, t_count, i_count, mark))

    return render_template(
        "views/student_statistics.html", results=results, title="Статистика"
    )
