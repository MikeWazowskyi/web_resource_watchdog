from flask import Blueprint

from .factories import create_database, create_flask_app
from .factories.celery_factory import create_celery_app
from .settings import Config

flask_app = create_flask_app(Config)
celery_app = create_celery_app(flask_app)
flask_app.extensions["celery"] = celery_app
db, migrate = create_database(flask_app)

api_v1 = Blueprint(
    name="api_v1",
    url_prefix="/api/v1",
    import_name=__name__,
)

from web_resource_watchdog.api_views import v1  # noqa

from . import error_handlers  # noqa
from . import tasks  # noqa

flask_app.register_blueprint(api_v1)
