import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from mixer.backend.flask import mixer as _mixer

load_dotenv()

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR))

try:
    from web_resource_watchdog import db, flask_app
    from web_resource_watchdog.models import WebResource
except NameError:
    raise AssertionError(
        "Application object not found.",
    )
except ImportError as exc:
    if any(obj in exc.name for obj in ["models", "WebResource"]):
        raise AssertionError("There is no WebResource model.")
    raise AssertionError("There is no SQLAlchemy object.")


@pytest.fixture
def default_app():
    """Fixture for flask app with context."""
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def _app(tmp_path):
    """Fixture for test database."""
    db_path = tmp_path / "test_db.sqlite3"
    db_uri = "sqlite:///" + str(db_path)
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": db_uri,
            "WTF_CSRF_ENABLED": False,
        }
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()
        db.session.close()


@pytest.fixture
def client(_app):
    """Fixture for flask app client."""
    return _app.test_client()


@pytest.fixture
def mixer():
    """Fixture for initializing the mixer with a Flask application."""
    _mixer.init_app(flask_app)
    return _mixer


@pytest.fixture
def short_python_url(mixer):
    """Fixture for creating a short URL for Python's official website."""
    return mixer.blend(WebResource, full_url="https://www.python.org")
