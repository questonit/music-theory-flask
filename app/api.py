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
from flask_login import current_user
from mongoengine.errors import ValidationError
import json

from app.models import Test, User, Result, get_id


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


@api.route("/user", methods=["GET"])
@jwt_required()
def user():
    email_user = get_jwt_identity()
    current_user = User.objects(email=email_user).first()

    data = {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
    }

    return jsonify(result="OK", data=data)


@api.route("/users", methods=["GET"])
@jwt_required()
def users():
    users = json.loads(User.objects.to_json())
    return jsonify(result="OK", data=users)


@api.route("/test", methods=["GET", "POST"])
@jwt_required()
def test():
    if request.method == "POST":
        name = request.json.get("name")
        section = request.json.get("section")
        question_array = request.json.get("question_array")

        teacher_id = request.json.get("teacher_id")
        # редактирование
        tid = request.json.get("test_id")

        if tid:
            if teacher_id is not None and not User.objects(user_id=teacher_id).first():
                return jsonify(result="ERROR", error="Учитель не найден")

            if test := Test.objects(test_id=tid).first():
                if name is not None:
                    test.name = name
                if section is not None:
                    test.section = section
                if question_array is not None:
                    test.question_array = question_array
                if teacher_id is not None:
                    test.teacher_id = teacher_id

                try:
                    test.save()
                except ValidationError:
                    return jsonify(result="ERROR", error="Ошибка валидации")

                return jsonify(result="OK", test_id=tid)

            return jsonify(result="ERROR", error="Тест не найден")

        # добавление
        if User.objects(user_id=teacher_id).first():
            test_id = get_id(Test.objects, "test_id")
            try:
                new_test = Test(
                    test_id=test_id,
                    name=name,
                    section=section,
                    question_array=question_array,
                    teacher_id=teacher_id,
                )

                new_test.save()
            except ValidationError:
                return jsonify(result="ERROR", error="Ошибка валидации")

            return jsonify(result="OK", test_id=test_id)

        return jsonify(result="ERROR", error="Учитель не найден")

    # GET
    # по id
    test_id = request.args.get("test_id")

    if test_id:
        tests = Test.objects(test_id=test_id)

        if tests:
            return jsonify(result="OK", data=json.loads(tests.to_json()))
        else:
            return jsonify(result="ERROR", error="Тест не найден")

    # по учителю
    teacher_id = request.args.get("teacher_id")

    if teacher_id:
        tests = Test.objects(teacher_id=teacher_id)

        if tests:
            return jsonify(result="OK", data=json.loads(tests.to_json()))
        else:
            return jsonify(result="ERROR", error="Тесты не найдены")

    # все тесты
    tests = Test.objects
    return jsonify(result="OK", data=json.loads(tests.to_json()))


@api.route("/test_delete", methods=["POST"])
@jwt_required()
def test_delete():
    test_id = request.json.get("test_id")

    if test := Test.objects(test_id=test_id).first():
        test.delete()
        return jsonify(result="OK")

    return jsonify(result="ERROR", error="Тест не найден")


@api.route("/result", methods=["GET", "POST"])
@jwt_required()
def result():
    if request.method == "POST":
        test_id = request.json.get("test_id")
        user_id = request.json.get("user_id")
        answer_wrong_array = request.json.get("answer_wrong_array")
        incorrect_count = request.json.get("incorrect_count")
        total_count = request.json.get("total_count")

        print(request.json)
        if (
            Test.objects(test_id=test_id).first()
            and User.objects(user_id=user_id).first()
        ):
            result_id = get_id(Result.objects, "result_id")
            try:
                new_result = Result(
                    result_id=result_id,
                    test_id=test_id,
                    user_id=user_id,
                    answer_wrong_array=answer_wrong_array,
                    incorrect_count=incorrect_count,
                    total_count=total_count,
                )

                new_result.save()
            except ValidationError:
                return jsonify(result="ERROR", error="Ошибка валидации")

            return jsonify(result="OK", result_id=result_id)

        return jsonify(result="ERROR", error="Учитель или тест не найден")

    result_id = request.args.get("result_id")

    if result_id:
        results = Result.objects(result_id=result_id)

        if results:
            return jsonify(result="OK", data=json.loads(results.to_json()))
        else:
            return jsonify(result="ERROR", error="Результат не найден")

    # по студенту
    user_id = request.args.get("user_id")

    if user_id:
        results = Result.objects(user_id=user_id)

        if results:
            return jsonify(result="OK", data=json.loads(results.to_json()))
        else:
            return jsonify(result="ERROR", error="Результаты не найдены")

    # все тесты
    results = Result.objects
    return jsonify(result="OK", data=json.loads(results.to_json()))


@api.route("/result_delete", methods=["POST"])
@jwt_required()
def result_delete():
    result_id = request.json.get("result_id")

    if result := Result.objects(result_id=result_id).first():
        result.delete()
        return jsonify(result="OK")

    return jsonify(result="ERROR", error="Результат не найден")


@api.route("/add_question", methods=["POST"])
def add_question():
    data = {}
    answers = []
    answers_false = []
    for el in request.json:
        data[el['name']] = el['value']


    for key, value in data.items():
        if key.startswith('answer') and value:
            if data.get(f"ch{key}"):
                answers.append(value)
            else:
                answers_false.append(value)
    
    count= len(answers)
    answers.extend(answers_false)

    if data['question_text'] == '' or len(answers) == 0 or count == 0:
        return jsonify(result="ERROR"), 400

    question = {
        "question_text": data['question_text'],
        "attachment_url": data['attachment_url'],
        "displayed_elements": [],
        "answer_array": answers,
        "ui_type": "stave",
        "generation_seed": {"count": count}
    }

    test_id = int(data['test_id'])
    question_id = int(data['question_id'])

    test = Test.objects(test_id=test_id).first()

    question_array = test.question_array
    if len(question_array) <= question_id:
        question_array.append(question)
    else: 
        question_array[question_id] = question

    test.question_array = question_array
    test.save()
    
    return jsonify(result="OK"), 200

