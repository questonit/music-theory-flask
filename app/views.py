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
from app.models import Result, Test, Theory, User, get_id

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
        tests.append((test.test_id, test.name, test.active or 0))

    return render_template("views/teacher_tests.html", tests=tests, title="Тесты")


@views.route("/tests/test")
@login_required
def test():
    if current_user.role != "teacher" and current_user.role != "admin":
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


@views.route("/theory_materials")
@login_required
def theory_list():

    if current_user.role != "student" and current_user.role != "teacher":
        return render_template("views/forbid.html", title="Ошибка"), 403

    theory_list = []

    theory_query = Theory.objects(teacher_id=current_user.user_id)
    if current_user.role == "student":
        theory_query = Theory.objects
    for th in theory_query:
        theory_list.append((th.theory_id, th.name))

    return render_template(
        "views/theory_list.html", theory_list=theory_list, title="Теория"
    )


@views.route("/theory_materials/theory", methods=["GET", "POST"])
@login_required
def theory():

    if current_user.role != "student" and current_user.role != "teacher":
        return render_template("views/forbid.html", title="Ошибка"), 403

    if request.method == "POST":
        theory_id = request.form.get("theory_id")
        name = request.form.get("theory_name")
        text = request.form.get("theory_text")

        if theory_id:
            th = Theory.objects(theory_id=theory_id).first()
            th.name = name
            th.text = text
            th.save()
        else:
            theory_id = get_id(Theory.objects, "theory_id")
            new_th = Theory(theory_id=theory_id, name=name, text=text, teacher_id=current_user.user_id)
            new_th.save()

        flash("Теория сохранена!")
        return redirect(url_for("views.theory_list"))

    theory_id = request.args.get("id")

    if theory_id:
        th = Theory.objects(theory_id=theory_id).first()
        theory_name = th.name
        theory_text = th.text

    else:
        theory_id = ""
        theory_name = ""
        theory_text = ""

    return render_template(
        "views/theory.html",
        theory_id=theory_id,
        theory_name=theory_name,
        theory_text=theory_text,
    )


@views.route("/accept_test", methods=["POST"])
@login_required
def accept_test():
    if current_user.role != "admin":
        return render_template("views/forbid.html", title="Ошибка"), 403

    test_id = request.form.get("test_id")
    test = Test.objects(test_id=test_id).first()

    test.active = 1
    test.save()
    flash("Тест подтвержден")
    return redirect(url_for("views.admin_tests"))


@views.route("/admin_tests")
@login_required
def admin_tests():
    if current_user.role != "admin":
        return render_template("views/forbid.html", title="Ошибка"), 403

    tests = []
    number = 0

    for test in Test.objects:
        number += 1
        teacher = User.objects(user_id = test.teacher_id).first()
        teacher_name = f"{teacher.first_name} {teacher.last_name}"
        test_active =  test.active or 0
        tests.append((number, test.test_id, test.name, teacher_name, test_active))

    return render_template("views/admin_tests.html", tests=tests, title="Тесты")  