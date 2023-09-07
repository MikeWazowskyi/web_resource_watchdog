import io
import zipfile

from pydantic import BaseModel, HttpUrl, ValidationError, field_validator

from web_resource_watchdog import Config


class CreateWebResource(BaseModel):
    """Pydantic schema for web resource model."""

    full_url: HttpUrl


class ZipFileValidator(BaseModel):
    """Pydantic schema for zip-file validation."""

    zip_file: bytes

    @field_validator("zip_file")
    def validate_zip_file(cls, value):
        """Validate the uploaded zip file.

        Parameters:
            value (bytes): The uploaded zip file as bytes.

        Returns:
            io.BytesIO: A BytesIO object representing
            the validated zip buffer.

        Raises:
            ValidationError: If the uploaded file is not a valid
            zip archive.
        """
        zip_buffer = io.BytesIO(value)
        try:
            with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                zip_ref.testzip()
            return zip_buffer
        except zipfile.BadZipFile:
            raise ValidationError(
                "Invalid zip file",
            )


def allowed_file(filename):
    """Check file extension in allowed extensions."""
    return ("." in filename) and (
        filename.rsplit(".", 1)[1].lower()
        in Config.ALLOWED_ARCHIVES_EXTENSIONS
    )
