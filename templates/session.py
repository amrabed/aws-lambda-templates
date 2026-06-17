from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class SessionManager:
    """Manages a configured requests Session with retries and connection pooling."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: list[int] | None = None,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ) -> None:
        """Initialize the SessionManager.

        Args:
            max_retries: Maximum number of retries.
            backoff_factor: Backoff factor for retries.
            status_forcelist: List of HTTP status codes to retry on.
            pool_connections: Number of connection pools to cache.
            pool_maxsize: Maximum number of connections to save in the pool.
        """
        self.session = Session()
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
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_session(self) -> Session:
        """Return the configured requests Session.

        Returns:
            The configured Session object.
        """
        return self.session
