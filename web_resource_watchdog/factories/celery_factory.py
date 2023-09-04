from celery import Celery, Task
from flask import Flask


def create_celery_app(flask_app: Flask) -> Celery:
    """Create and configure a Celery for integration with a Flask."""

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(flask_app.name, task_cls=FlaskTask)
    celery_app.config_from_object(flask_app.config["CELERY"])
    celery_app.set_default()
    return celery_app
