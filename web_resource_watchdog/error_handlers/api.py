from http import HTTPStatus

from flask import jsonify
from pydantic import ValidationError

from web_resource_watchdog import api_v1
from web_resource_watchdog.errors import InvalidAPIUsage


@api_v1.errorhandler(InvalidAPIUsage)
def invalid_api_usage_handler(error: InvalidAPIUsage):
    """
    Handle the error for InvalidAPIUsage.

    Returns a tuple with information about the error details and status code.
    """
    return jsonify(error.to_dict()), error.status_code


@api_v1.errorhandler(ValidationError)
def data_validation_failed_handler(error: ValidationError):
    """
    Handle the error for ValidationError.

    Returns a dictionary with information about the error details.
    """
    return error.json(), HTTPStatus.BAD_REQUEST
