import email
from flask import current_app, Blueprint, render_template
from flask_login import current_user, login_required
from app.models import User

views = Blueprint("views", __name__, url_prefix="/")


@views.route("/")
def index():
    return render_template("views/index.html")

@views.route("/config")
def config():
    return str(current_app.config['DEBUG']), current_app.config['JWT_SECRET_KEY']


@views.route("/profile")
@login_required
def profile():

    return render_template(
        "views/profile.html", name=f"{current_user.first_name} {current_user.last_name}"
    )
