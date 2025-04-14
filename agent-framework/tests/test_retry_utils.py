import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class InternalServerError(Exception):
    pass


class APIError(Exception):
    pass


@retry(
    retry=retry_if_exception_type(
        (InternalServerError, APIError, requests.exceptions.RequestException)
    ),
    wait=wait_exponential(multiplier=4, min=1, max=60),
    stop=stop_after_attempt(3),
    before_sleep=lambda retry_state: print(
        f"Attempt {retry_state.attempt_number} failed, retrying in {retry_state.next_action.sleep} seconds..."
    ),
    before=lambda retry_state: (
        (
            retry_state.kwargs.update({"is_retry": True})
            if retry_state.attempt_number > 1
            else None
        ),
        print(
            f"\n=== RETRY ATTEMPT {retry_state.attempt_number} ===\n"
            f"Is retry: {retry_state.kwargs.get('is_retry')}"
        ),
    )[1],
)
def my_function(is_retry=False):
    print(f"Function called with is_retry={is_retry}")
    raise InternalServerError("Simulated API failure")


# Run the function to see retry behavior
try:
    my_function()
except InternalServerError:
    print("Function ultimately failed after retries")
