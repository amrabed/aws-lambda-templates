from typing import Any

from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class ApiSession:
    """Manages a configured requests Session with retries and connection pooling."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        timeout: int = 10,
        status_forcelist: list[int] | None = None,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ) -> None:
        """Initialize the ApiSession.

        Args:
            max_retries: Maximum number of retries.
            backoff_factor: Backoff factor for retries.
            timeout: Preset timeout for requests in seconds.
            status_forcelist: List of HTTP status codes to retry on.
            pool_connections: Number of connection pools to cache.
            pool_maxsize: Maximum number of connections to save in the pool.
        """
        self._timeout = timeout
        self._session = Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist or [429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def get(self, url: str, **kwargs: Any) -> Response:
        """Perform a GET request with the preset timeout.

        Args:
            url: The URL to request.
            **kwargs: Additional arguments passed to the session.get call.

        Returns:
            The Response object.
        """
        kwargs.setdefault("timeout", self._timeout)
        return self._session.get(url, **kwargs)
