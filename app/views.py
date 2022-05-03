from flask import current_app, Blueprint
views = Blueprint('views', __name__, url_prefix='/')

@views.route('/')
def index():
    return 'Hello world'