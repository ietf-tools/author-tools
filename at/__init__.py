from flask import Flask
from flask_cors import CORS


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    if config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(config)

    from . import api
    app.register_blueprint(api.bp)

    return app
