from flask import Flask
from flask_cors import CORS


def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    if config is None:
        app.config.from_object('at.config')
    else:
        app.config.from_mapping(config)

    from . import api
    app.register_blueprint(api.bp)

    return app
