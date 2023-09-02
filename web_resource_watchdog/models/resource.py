from http import HTTPStatus
from typing import Any
from urllib.parse import urlparse

from flask_sqlalchemy.session import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from web_resource_watchdog import db
from web_resource_watchdog.errors import InvalidAPIUsage


class WebResource(db.Model):
    """Model for representing web resources.

    Attributes:
        id (int): The primary key of the web resource.
        full_url (str): The full URL of the web resource.
        protocol (str): The protocol used (e.g., http, https).
        domain (str): The domain of the web resource.
        domain_zone (str): The domain zone (e.g., .com, .org).
        url_path (str): The path part of the URL.
        query_params (str): The query parameters of the URL.
        screenshot (bytes, optional): Binary data for a screenshot,
            if available.
        fail_count (int): The count of failures for this resource.
        status_codes (relationship): Relationship to the associated web
            resource status entries.
    """

    id = db.Column(db.Integer, primary_key=True)
    full_url = db.Column(db.String, nullable=False, unique=True)
    protocol = db.Column(db.String, nullable=False)
    domain = db.Column(db.String, nullable=False)
    domain_zone = db.Column(db.String, nullable=False)
    url_path = db.Column(db.String)
    query_params = db.Column(db.String)
    screenshot = db.Column(db.LargeBinary, nullable=True)
    fail_count = db.Column(db.Integer, default=0, nullable=False)
    status_codes = relationship("WebResourceStatus", back_populates="resource")

    @classmethod
    def create(
        cls,
        data: dict,
        commit: bool = True,
        session: Session | None = None,
    ) -> "WebResource":
        """Create a new WebResource instance based on the provided data."""
        web_resource = cls(**data)
        web_resource_status = WebResourceStatus()
        web_resource.status_codes = web_resource_status
        web_resource.parse_url()
        if commit:
            web_resource.save(session)
        return web_resource

    def save(self, session: Session = None) -> None:
        """Save the WebResource instance to the database."""
        if session is None:
            session = db.session
        try:
            session.add(self)
            session.commit()
        except IntegrityError as error:
            raise InvalidAPIUsage(
                message=str(error),
                status_code=HTTPStatus.BAD_REQUEST,
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert the WebResource instance to a dictionary."""
        return {
            column.key: getattr(self, column.key)
            for column in self.__table__.columns
        }

    def parse_url(self) -> None:
        """Parse the full_url to populate other URL-related attributes."""
        parsed_url = urlparse(self.full_url)
        self.protocol = parsed_url.scheme
        self.url_path = parsed_url.path
        self.query_params = parsed_url.query
        self.domain, self.domain_zone = parsed_url.netloc.rsplit(".", 1)


class WebResourceStatus(db.Model):
    """Model for tracking the status of web resources.

    Attributes:
        id (int): The primary key of the web resource status entry.
        resource_id (int): The foreign key referencing the associated
            web resource.
        status_code (int, optional): The HTTP status code received for
            the resource.
        request_time (datetime): The timestamp of the request to the
            web resource.
        is_available (bool): Indicates whether the resource is currently
            available.
        is_watched (bool): Indicates whether the resource is being actively
            monitored.

    Relationships:
        resource: A reference to the associated web resource.
    """

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey(WebResource.id))
    status_code = db.Column(db.Integer, nullable=True)
    request_time = db.Column(
        db.DateTime(timezone=True), server_default=func.now()
    )
    is_available = db.Column(db.Boolean, default=False)
    is_watched = db.Column(db.Boolean, default=True)
    resource = relationship("WebResource", back_populates="status_codes")
