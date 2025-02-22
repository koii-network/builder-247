"""Middleware for Flask application."""

from functools import wraps
from flask import request, make_response, jsonify
import logging

logger = logging.getLogger(__name__)


def add_error_headers(fn):
    """Middleware to add error messages to response headers."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            response = fn(*args, **kwargs)

            # If response is a tuple (response, status_code)
            if isinstance(response, tuple):
                response_obj, status_code = response
            else:
                response_obj = response
                status_code = 200 if not hasattr(response, 'status_code') else response.status_code

            # Convert response to a Response object if it isn't already
            if not hasattr(response_obj, 'headers'):
                response_obj = make_response(response_obj)

            # For error responses, add the error message to headers
            if status_code >= 400:
                error_msg = ""
                if isinstance(response_obj.get_json(), dict):
                    error_msg = response_obj.get_json().get('error') or response_obj.get_json().get('message', '')
                elif isinstance(response_obj.get_data(), (str, bytes)):
                    error_msg = str(response_obj.get_data())

                if error_msg:
                    response_obj.headers['X-Error-Message'] = error_msg
                    logger.error(f"{request.method} {request.path} - {status_code} - {error_msg}")

            return response_obj, status_code

        except Exception as e:
            logger.exception("Error in request handler")
            error_response = make_response(jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500)
            error_response.headers['X-Error-Message'] = str(e)
            return error_response

    return wrapper
