from http import HTTPStatus

from celery import current_app
from flask import jsonify, request

from web_resource_watchdog import Config, api_v1
from web_resource_watchdog.errors import InvalidAPIUsage
from web_resource_watchdog.models.resource import WebResource
from web_resource_watchdog.schemas.resource import (
    CreateWebResource,
    ZipFileValidator,
    allowed_file,
)
from web_resource_watchdog.tasks.resource import (
    find_resources,
    save_resources_to_db,
)


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
    task = (find_resources.s(file_data) | save_resources_to_db.s())()
    return (
        jsonify(
            {"message": "Zip file processing started.", "task_id": task.id}
        ),
        HTTPStatus.CREATED,
    )


@api_v1.route("/get_parse_status/<string:task_id>/", methods=["GET"])
def get_parse_status(task_id: str):
    """
    Retrieve the status and result of a task for parsing a zip file.

    Args:
        task_id (str): The unique identifier of the asynchronous task to
        retrieve information for.

    Returns:
        dict[str, object]: A dictionary of information about the task:
            - "status" (str): Status of the task: "pending", "success",
            or "error".
            - "message" (str): A message describing the task status
            or error.
    """
    try:
        broker = current_app.backend.client
        error_key = Config.ERROR_KEY.format(task_id=task_id)
        parse_errors = list(
            map(
                lambda error: error.decode("utf-8"),
                broker.lrange(error_key, 0, -1),
            )
        )
        result = find_resources.AsyncResult(task_id)
        if result.successful():
            response = {
                "status": "completed",
                "message": "Task executed successfully",
            }
            if parse_errors:
                response["message"] = "Task executed with errors"
                response["errors"] = parse_errors
            return response, HTTPStatus.OK
        elif result.failed():
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Task encountered an error",
                        "error": result.traceback,
                    }
                ),
                HTTPStatus.OK,
            )
        else:
            return (
                jsonify(
                    {"status": "pending", "message": "Task is still pending"}
                ),
                HTTPStatus.OK,
            )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Internal server error",
                    "error": str(e),
                }
            ),
            HTTPStatus.OK,
        )
