from http import HTTPStatus

from flask import jsonify, request

from web_resource_watchdog import api_v1
from web_resource_watchdog.errors import InvalidAPIUsage
from web_resource_watchdog.models.resource import WebResource
from web_resource_watchdog.schemas.resource import (
    CreateWebResource,
    ZipFileValidator,
    allowed_file,
)
from web_resource_watchdog.tasks.resource import parse_zip_file, save_to_db


@api_v1.route("/add_resource/", methods=["POST"])
def add_resource():
    """
    Create a new web resource.

    This endpoint allows you to create a new web resource by providing JSON
    data in the request body.

    Returns:
        dict: A dictionary containing the details of the newly created web
        resource;
        int: HTTP response status code.
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


@api_v1.route("/add_resource_from_zip/", methods=["POST"])
def add_resource_from_zip():
    """
    Create a new web resources from zip file.

    This endpoint allows you to create a new web resources by providing
    zip file in the request body.

    Returns:
        dict: A dictionary containing the details of the newly created web
        resource;
        int: HTTP response status code.
    Raises:
        InvalidAPIUsage: If the request body is empty or JSON data
        validation fails.
    """
    if "file" not in request.files:
        raise InvalidAPIUsage(
            "No file part.", status_code=HTTPStatus.BAD_REQUEST
        )
    file = request.files["file"]
    if file.filename == "":
        raise InvalidAPIUsage(
            "File is empy.", status_code=HTTPStatus.BAD_REQUEST
        )
    if not allowed_file(file.filename):
        raise InvalidAPIUsage(
            "File extension is not allowed.",
            status_code=HTTPStatus.BAD_REQUEST,
        )
    file_data = file.read()
    ZipFileValidator.validate_zip_file(file_data)
    task = parse_zip_file.apply_async((file_data,), link=save_to_db.s())
    return (
        jsonify(
            {"message": "Zip file processing started.", "task_id": task.id}
        ),
        HTTPStatus.CREATED,
    )


@api_v1.route("/get_parse_status/<string:task_id>/", methods=["GET"])
def task_result(task_id: str) -> dict[str, object]:
    """
    Retrieve the status and result of a task for parsing a zip file.

    Args:
        task_id (str): The unique identifier of the asynchronous task to
        retrieve information for.

    Returns:
        dict[str, object]: A dictionary of information about the task:
            - "ready" (bool): Indicates whether the task has completed
              (True) or is still pending (False).
            - "successful" (bool): Indicates whether the task was executed
               successfully (True) or had an error (False).
    """
    result = parse_zip_file.AsyncResult(task_id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
    }
