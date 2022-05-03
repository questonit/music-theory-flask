from flask import Flask
from . import config

def create_app(config=config.DevelopementConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    from .db import db
    db.init_app(app)

    from .views import views
    app.register_blueprint(views)

    return app