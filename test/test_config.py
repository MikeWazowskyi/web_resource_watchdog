import os


def test_config(default_app):
    """Test the application configuration."""
    assert default_app.config["SQLALCHEMY_DATABASE_URI"] == os.getenv(
        "SQLALCHEMY_DATABASE_URI"
    ), (
        "Check, that config key SQLALCHEMY_DATABASE_URI "
        "has value with database settings"
    )
    assert default_app.config["SECRET_KEY"] == os.getenv(
        "SECRET_KEY"
    ), "Check, that config key SECRET_KEY has value"
