import re
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    current_user,
    logout_user,
)
from flask import (
    current_app,
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import User, get_id

auth = Blueprint("auth", __name__, url_prefix="/auth")

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Пожалуйста, авторизируйтесь, чтобы открыть эту страницу."


@login_manager.user_loader
def load_user(id):
    return User.objects(id=id).first()


def check_email(email):
    pattern = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"

    if re.match(pattern, email) is not None:
        return True

    return False


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")

        user = User.objects(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            return redirect(url_for("views.profile"))

        flash("Неверный email или пароль")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("views.profile"))

    if request.method == "POST":
        email = request.form.get("email")

        if not check_email(email):
            flash("Неверный формат email")
            return redirect(url_for("auth.signup"))

        if User.objects(email=email).first():
            flash("Данный email уже используется")
            return redirect(url_for("auth.signup"))

        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        role = request.form.get("role")

        if not (email and password and first_name and last_name):
            flash("Не все поля заполнены")
            return redirect(url_for("auth.signup"))

        user_id = get_id(User.objects, "user_id")

        new_user = User(
            user_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role if role == "student" else "teacher_w",
        )
        new_user.set_password(password=password)
        new_user.save()

        login_user(new_user)

        return redirect(url_for("views.profile"))

    return render_template("auth/signup.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.index"))


@auth.route("/accept-teacher", methods=["POST"])
@login_required
def accept_teacher():
    if current_user.role != "admin":
        return render_template("views/forbid.html", title="Ошибка"), 403

    user_id = request.form.get("user_id")
    teacher = User.objects(user_id=user_id).first()

    teacher.role = "teacher"
    teacher.save()
    flash("Роль подтверждена")
    return redirect(url_for("views.admin_users"))
