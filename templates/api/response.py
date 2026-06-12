from json import dumps

from aws_lambda_powertools.event_handler.api_gateway import Response

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


class JsonResponse(Response):
    """An HTTP response with JSON body and security headers."""

    def __init__(self, body: dict | str, status_code: int = 200) -> None:
        """Initialize the JSON response.

        Args:
            body: The response body as a dictionary or JSON string.
            status_code: The HTTP status code.
        """
        super().__init__(
            status_code=status_code,
            body=body if isinstance(body, str) else dumps(body),
            content_type="application/json",
            headers=SECURITY_HEADERS,
        )
