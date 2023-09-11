import re

from celery import shared_task

from web_resource_watchdog.models import WebResource
from web_resource_watchdog.utils.zipfile import parse_zip_file


@shared_task
def find_resources(file: bytes, pattern: re.Pattern = None) -> list[str]:
    """Find all urls in file."""
    parse_data, errors = parse_zip_file(file, pattern)
    if parse_data:
        return parse_data


@shared_task
def save_resources_to_db(data: list[str]) -> None:
    """Save Web Resource data to database."""
    if data:
        WebResource.bulk_create(data)
