# Add common Pytest fixtures here
import sys
from unittest.mock import MagicMock

# aws_xray_sdk is not installed in the test environment; stub it out before
# any handler module is imported so that Powertools Tracer initialises cleanly.
sys.modules.setdefault("aws_xray_sdk", MagicMock())
sys.modules.setdefault("aws_xray_sdk.core", MagicMock())
