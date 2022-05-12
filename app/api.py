from flask import (
    current_app,
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    Response,
)
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
)

from app.models import User, get_id

api = Blueprint("api", __name__, url_prefix="/api")
jwt = JWTManager()


@api.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.objects(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=email)
        return jsonify(result="OK", access_token=access_token)

    return jsonify(result="ERROR", error="Неверный email или пароль")


@api.route("/signup", methods=["POST"])
def signup():
    email = request.json.get("email", None)

    if User.objects(email=email).first():
        return jsonify(result="ERROR", error="Данный email уже используется")

    password = request.json.get("password", None)
    first_name = request.json.get("first_name", None)
    last_name = request.json.get("last_name", None)
    role = request.json.get("role", None)

    if not (email and password and first_name and last_name):
        return jsonify(result="ERROR", error="Не все поля заполнены")

    user_id = get_id(User.objects, "user_id")

    new_user = User(
        user_id=user_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
    )
    new_user.set_password(password=password)
    new_user.save()

    access_token = create_access_token(identity=email)
    return jsonify(result="OK", access_token=access_token)
