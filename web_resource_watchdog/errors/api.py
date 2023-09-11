from http import HTTPStatus


class InvalidAPIUsage(Exception):
    """Invalid API usage exception."""

    status_code = HTTPStatus.NOT_FOUND

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code:
            self.status_code = status_code

    def to_dict(self):
        """Convert InvalidAPIUsage instance to dictionary."""
        return dict(error=self.message)

    def __repr__(self):
        """Convert InvalidAPIUsage instance to sting."""
        return f"{self.__class__}: {self.message}, {self.status_code}"
