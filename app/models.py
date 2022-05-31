from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db import db


def get_id(objects, id_name):
    max_item = objects.order_by(f"-{id_name}").limit(-1).first()
    if max_item:
        return max_item[id_name] + 1
    return 0


class User(db.Document, UserMixin):
    user_id = db.IntField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password_hash = db.StringField(reqired=True)

    first_name = db.StringField(max_length=50, required=True)
    last_name = db.StringField(max_length=50, required=True)

    role = db.StringField(
        choices=["admin", "teacher", "teacher_w", "student"], required=True
    )

    def __repr__(self):
        return "<{}:{}>".format(self.user_id, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Question(db.Document):
    # question_id = db.IntField(required=True, unique=True)
    question_text = db.StringField()
    attachment_url = db.StringField()

    answer_array = db.ListField(db.StringField())
    ui_type = db.StringField()
    generation_seed = db.DictField()
    displayed_elements = db.ListField(db.DictField())


class Test(db.Document):
    test_id = db.IntField(required=True, unique=True)
    name = db.StringField()
    section = db.ListField(db.StringField())
    question_array = db.ListField(db.DictField())
    teacher_id = db.IntField()
    active = db.IntField()


class Result(db.Document):
    result_id = db.IntField(required=True, unique=True)

    user_id = db.IntField()
    test_id = db.IntField()

    answer_wrong_array = db.ListField(db.DictField())
    """
    {
        question_text: string
        answers: array
    }
    """

    incorrect_count = db.IntField()
    total_count = db.IntField()


class Theory(db.Document):
    theory_id = db.IntField(required=True, unique=True)

    teacher_id = db.IntField()
    name = db.StringField()
    text = db.StringField()
