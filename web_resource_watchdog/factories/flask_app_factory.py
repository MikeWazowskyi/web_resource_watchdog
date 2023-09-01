from typing import Type  # noqa D104

from flask import Flask

from web_resource_watchdog.settings import Config


def create_flask_app(config: Type[Config]) -> Flask:
    """Create Flask application from Config class."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(config)
    return flask_app
