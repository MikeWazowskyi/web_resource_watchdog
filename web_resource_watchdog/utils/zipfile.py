import io
import re
import zipfile

URL_PATTERN = re.compile(
    (
        r"\b(?:http|ftp|https)://(?:[\w_-]+(?:(?:\.[\w_-]+)+))"
        r"(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])\b"
    )
)


def parse_zip_file(
    file: bytes,
    pattern: re.Pattern | None = None,
) -> tuple[list[str], list[str]]:
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
    return list(result), errors
