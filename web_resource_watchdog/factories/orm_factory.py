from typing import Tuple

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def create_database(flask_app: Flask) -> Tuple[SQLAlchemy, Migrate]:
    """Create SQLAlchemy ORM and migrations."""
    database = SQLAlchemy(flask_app)
    migrate = Migrate(flask_app, database)
    return database, migrate
