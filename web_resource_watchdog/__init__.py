from flask import Blueprint

from .factories import create_database, create_flask_app
from .settings import Config

flask_app = create_flask_app(Config)
db, migrate = create_database(flask_app)

api_v1 = Blueprint(
    name="api_v1",
    url_prefix="/api/v1",
    import_name=__name__,
)

from web_resource_watchdog.api_views import v1  # noqa

from . import error_handlers  # noqa

flask_app.register_blueprint(api_v1)
