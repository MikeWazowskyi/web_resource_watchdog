import os  # noqa D104

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    if FLASK_ENV == "development":
        SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "SQLALCHEMY_DATABASE_URI",
            "sqlite:///db.sqlite3",
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_APP = os.getenv("FLASK_APP", "web_resource_watchdog")
    CELERY = dict(
        broker_url=os.getenv("BROKER_URL_HOST", "redis://localhost"),
        result_backend=os.getenv("BACKEND_RESULT_HOST", "redis://localhost"),
    )
    ALLOWED_ARCHIVES_EXTENSIONS = {
        "zip",
    }
    ERROR_KEY = "task_errors:{task_id}"
