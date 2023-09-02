from http import HTTPStatus

from errors import InvalidAPIUsage
from flask import jsonify, request
from models.resource import WebResource
from schemas.resource import CreateWebResource

from web_resource_watchdog import api_v1


@api_v1.route("/add_resource/", methods=["POST"])
def add_resource():
    """
    Create a new web resource.

    This endpoint allows you to create a new web resource by providing JSON
    data in the request body.

    Returns:
        dict: A dictionary containing the details of the newly created web
        resource.
    Raises:
        InvalidAPIUsage: If the request body is empty or JSON data
        validation fails.
    """
    if not request.data:
        raise InvalidAPIUsage(
            "Request body is empty",
            status_code=HTTPStatus.BAD_REQUEST,
        )
    CreateWebResource.model_validate_json(request.data)
    web_resource = WebResource.create(request.get_json())
    return jsonify(web_resource.to_dict()), HTTPStatus.CREATED
