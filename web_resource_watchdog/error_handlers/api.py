from errors import InvalidAPIUsage
from flask import jsonify

from web_resource_watchdog import api_v1


@api_v1.errorhandler(InvalidAPIUsage)
def invalid_usage(error: InvalidAPIUsage):
    """
    Handle the error for InvalidAPIUsage.

    Returns a tuple with information about the error
    details and status code.
    """
    return jsonify(error.to_dict()), error.status_code
