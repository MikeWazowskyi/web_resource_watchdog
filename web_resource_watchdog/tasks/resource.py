import io
import logging
import re
import zipfile

from celery import shared_task

from web_resource_watchdog.models import WebResource

URL_PATTERN = re.compile(
    (
        r"\b(?:http|ftp|https)://(?:[\w_-]+(?:(?:\.[\w_-]+)+))"
        r"(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])\b"
    )
)


@shared_task
def parse_zip_file(file: bytes, pattern: re.Pattern = None) -> list[str]:
    """Parse a zip file containing text files and extracts URLs."""
    if pattern is None:
        pattern = URL_PATTERN
    zip_buffer = io.BytesIO(file)
    result = set()
    try:
        with zipfile.ZipFile(zip_buffer, "r") as zipf:
            for filename in zipf.namelist():
                with zipf.open(filename) as file_in_zip:
                    try:
                        file = file_in_zip.read().decode("utf-8")
                    except UnicodeDecodeError as decode_error:
                        logging.error(decode_error)
                    else:
                        finds = pattern.findall(file)
                        if finds:
                            result.update(finds)
    except zipfile.BadZipFile:
        pass
    return list(result)


@shared_task
def save_to_db(data: list[str]) -> None:
    """Save Web Resource data to database."""
    try:
        WebResource.bulk_create(data)
    except Exception:
        pass
