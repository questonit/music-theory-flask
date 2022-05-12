from flask import Flask

from app import config
from app.db import db
from app.auth import login_manager, auth
from app.views import views
from app.api import jwt, api


def create_app(config=config.DevelopementConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(api)

    return app
