import re

from celery import current_app, shared_task

from web_resource_watchdog.models import WebResource
from web_resource_watchdog.settings import Config
from web_resource_watchdog.utils.zipfile import parse_zip_file


@shared_task
def find_resources(file: bytes, pattern: re.Pattern = None) -> list[str]:
    """Find all urls in file."""
    parse_data, errors = parse_zip_file(file, pattern)
    if parse_data:
        return parse_data


@shared_task(bind=True)
def save_resources_to_db(self, data) -> None:
    """Save Web Resource data to database."""
    parse_data = data.get("data", None)
    errors = data.get("errors", None)
    if errors:
        broker = current_app.backend.client
        error_key = Config.ERROR_KEY.format(task_id=self.request.id)
        for error in errors:
            broker.lpush(error_key, error)
    if parse_data:
        WebResource.bulk_create(parse_data)
