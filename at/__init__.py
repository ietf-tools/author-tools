from os import getenv

from flask import Flask
from flask_cors import CORS
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.flask import FlaskIntegration


def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    if config is None:
        app.logger.info('Using configuration settings from at/config.py')
        app.config.from_object('at.config')
    else:
        app.logger.info('Using configuration settings from {}'.format(
            str(config)))
        app.config.from_mapping(config)

    from . import api
    app.register_blueprint(api.bp)

    SENTRY_DSN = getenv('SENTRY_DSN')

    if SENTRY_DSN:
        sentry_init(
                dsn=SENTRY_DSN,
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0)
        app.logger.info('Sentry is enabled.')
    else:
        app.logger.info('Sentry is disabled.')

    return app
