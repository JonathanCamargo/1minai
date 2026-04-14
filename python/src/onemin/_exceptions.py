"""Exception hierarchy for the 1min.ai SDK.

All SDK exceptions inherit from OneMinError.

Hierarchy:
    OneMinError (base)
    ├── APIError (HTTP-level errors, has status_code and request_id)
    │   ├── AuthenticationError (401)
    │   ├── RateLimitError (429)
    │   ├── NotFoundError (404)
    │   ├── BadRequestError (400)
    │   └── InternalServerError (5xx)
    └── ConnectionError (network-level, NOT an APIError)
        └── TimeoutError (connection timeout)

Note: Never include request body or API key in error messages (per D-10).
"""


class OneMinError(Exception):
    """Base class for all 1min.ai SDK errors."""


class APIError(OneMinError):
    """Raised when the API returns an error HTTP status code.

    Args:
        message: Human-readable error message from the API response.
        status_code: HTTP status code of the response.
        request_id: Optional request identifier from the x-request-id header.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        request_id: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.request_id = request_id
        super().__init__(f"HTTP {status_code}: {message}")


class AuthenticationError(APIError):
    """Raised when the API returns a 401 Unauthorized response.

    This typically means the API key is invalid or missing.
    """


class RateLimitError(APIError):
    """Raised when the API returns a 429 Too Many Requests response."""


class NotFoundError(APIError):
    """Raised when the API returns a 404 Not Found response."""


class BadRequestError(APIError):
    """Raised when the API returns a 400 Bad Request response."""


class InternalServerError(APIError):
    """Raised when the API returns a 5xx Server Error response."""


class ConnectionError(OneMinError):
    """Raised when a network-level error occurs (not an HTTP error).

    This is a network transport error, not a remote API error.
    It is NOT a subclass of APIError.
    """


class TimeoutError(ConnectionError):
    """Raised when a request times out.

    Extends ConnectionError (which extends OneMinError), not APIError.
    """
