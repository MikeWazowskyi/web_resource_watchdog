import io
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
def parse_zip_file(file: bytes, pattern: re.Pattern = None) -> dict[str, list]:
    """Parse a zip file containing text files and extracts URLs."""
    if pattern is None:
        pattern = URL_PATTERN
    zip_buffer = io.BytesIO(file)
    result = set()
    errors = []
    with zipfile.ZipFile(zip_buffer, "r") as zipf:
        for file in zipf.infolist():
            if file.is_dir():
                continue
            with zipf.open(file) as file_in_zip:
                try:
                    file_data = file_in_zip.read().decode("utf-8")
                except UnicodeDecodeError:
                    errors.append(f"Cannot decode file {file.filename}.")
                else:
                    finds = pattern.findall(file_data)
                    if finds:
                        result.update(finds)
                    else:
                        errors.append(f"File {file.filename} has no urls.")
    parse_data = {"data": list(result)}
    if errors:
        parse_data["errors"] = errors
    return parse_data


@shared_task
def save_resources_to_db(data: dict[str, list]) -> None:
    """Save Web Resource data to database."""
    parse_data = data.get("data", None)
    if parse_data:
        WebResource.bulk_create(parse_data)
