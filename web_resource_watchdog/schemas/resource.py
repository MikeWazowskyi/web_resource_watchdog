from pydantic import BaseModel, HttpUrl


class CreateWebResource(BaseModel):
    """Pydantic schema for web resource model."""

    full_url: HttpUrl
