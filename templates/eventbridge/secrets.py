"""Secrets management for the EventBridge template."""

from typing import cast

from aws_lambda_powertools.utilities.parameters import SecretsProvider
from botocore.config import Config


class SecretManager:
    """Wrapper around SecretsProvider with configurable retries and caching."""

    def __init__(self, max_retries: int = 3, max_age: int = 60) -> None:
        """Initialize the SecretManager.

        Args:
            max_retries: Maximum number of retry attempts for AWS service calls.
            max_age: Maximum age of the cached secret in seconds.
        """
        self._max_age = max_age
        config = Config(tcp_keepalive=True, retries={"max_attempts": max_retries, "mode": "standard"})
        self._provider = SecretsProvider(boto_config=config)

    def get(self, name: str) -> str:
        """Retrieve a secret by name.

        Args:
            name: The name of the secret to retrieve.

        Returns:
            The secret value as a string.
        """
        return cast(str, self._provider.get(name, max_age=self._max_age))
