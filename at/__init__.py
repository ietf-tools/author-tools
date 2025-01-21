from logging import ERROR as LOG_ERROR
from os import getenv

from flask import Flask
from flask_cors import CORS
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    if config is None:
        app.logger.info("Using configuration settings from at/config.py")
        app.config.from_object("at.config")
    else:
        app.logger.info(f"Using configuration settings from {str(config)}")
        app.config.from_mapping(config)

    from . import api

    app.register_blueprint(api.bp)

    if site_url := getenv("SITE_URL"):
        app.logger.info("Using SITE_URL from ENV.")
        app.config["SITE_URL"] = site_url
    elif "SITE_URL" not in app.config.keys():
        app.logger.info("SITE_URL not set. Using default.")
        app.config["SITE_URL"] = "http://localhost"

    app.logger.info(f"SITE_URL: {app.config['SITE_URL']}")

    if sentry_dsn := getenv("SENTRY_DSN"):
        sentry_init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                LoggingIntegration(level=LOG_ERROR, event_level=LOG_ERROR),
            ],
            traces_sample_rate=1.0,
        )
        app.logger.info("Sentry is enabled.")
    else:
        app.logger.info("Sentry is disabled.")

    return app
