from .factories import create_flask_app  # noqa D104
from .settings import Config

flask_app = create_flask_app(Config)
