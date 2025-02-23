"""Middleware for Flask application."""

from functools import wraps
from flask import request, make_response, jsonify
from src.utils.logging import log_key_value, log_error


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
                status_code = (
                    200
                    if not hasattr(response, "status_code")
                    else response.status_code
                )

            # Convert response to a Response object if it isn't already
            if not hasattr(response_obj, "headers"):
                response_obj = make_response(response_obj)

            # Log the request and response
            error_msg = ""
            if status_code >= 400 and isinstance(response_obj.get_json(), dict):
                error_msg = response_obj.get_json().get(
                    "error"
                ) or response_obj.get_json().get("message", "")

            # Format: [REQ] METHOD /path STATUS error_msg duration
            duration = request.environ.get("REQUEST_TIME", 0) * 1000  # Convert to ms
            status_color = "\033[32m" if status_code < 400 else "\033[31m"
            log_key_value(
                "[REQ]",
                f"{request.method} {request.path} {status_color}{status_code}\033[0m {error_msg} {duration}ms",
            )

            # For error responses, add the error message to headers
            if status_code >= 400:
                if error_msg:
                    response_obj.headers["X-Error-Message"] = error_msg
                    log_error(
                        Exception(error_msg),
                        context=f"Error handling request {request.method} {request.path}",
                        include_traceback=False,
                    )

            return response_obj, status_code

        except Exception as e:
            error_msg = str(e)
            status_code = 500
            duration = request.environ.get("REQUEST_TIME", 0) * 1000

            # Log the error without stack trace for API errors
            log_error(
                e,
                context=f"Unexpected error handling request {request.method} {request.path}",
                include_traceback=False,
            )

            # Format error response
            error_response = make_response(
                jsonify({"error": "Internal server error", "message": error_msg}),
                status_code,
            )
            error_response.headers["X-Error-Message"] = error_msg

            # Log request with error
            log_key_value(
                "[REQ]",
                f"{request.method} {request.path} \033[31m{status_code}\033[0m {error_msg} {duration}ms",
            )

            return error_response, status_code

    return wrapper
