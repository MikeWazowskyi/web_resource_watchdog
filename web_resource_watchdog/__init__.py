from .factories import create_database, create_flask_app  # noqa D104
from .settings import Config

flask_app = create_flask_app(Config)
db, migrate = create_database(flask_app)
