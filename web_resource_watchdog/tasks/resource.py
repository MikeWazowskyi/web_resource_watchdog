import re

from celery import shared_task

from web_resource_watchdog.models import WebResource
from web_resource_watchdog.utils.zipfile import parse_zip_file


@shared_task
def find_resources(file: bytes, pattern: re.Pattern = None) -> dict[str, list]:
    """Find all urls in file."""
    return parse_zip_file(file, pattern)


@shared_task
def save_resources_to_db(data: dict[str, list]) -> None:
    """Save Web Resource data to database."""
    parse_data = data.get("data", None)
    if parse_data:
        WebResource.bulk_create(parse_data)
