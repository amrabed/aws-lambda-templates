# Add common Pytest fixtures here
import sys
from unittest.mock import MagicMock, patch

# aws_xray_sdk is not installed in the test environment; stub it out before
# any handler module is imported so that Powertools Tracer initialises cleanly.
sys.modules.setdefault("aws_xray_sdk", MagicMock())
sys.modules.setdefault("aws_xray_sdk.core", MagicMock())

# Patch SecretsProvider globally so that handler.py can be imported without
# real AWS credentials. Individual tests override the instance via patch.object.
patch("aws_lambda_powertools.utilities.parameters.SecretsProvider", MagicMock()).start()

# Clear any previously cached (broken) handler modules so they re-import cleanly.
# This runs at conftest import time, before any test collection or execution.
for _mod in list(sys.modules):
    if _mod.startswith("templates.eventbridge") or _mod == "templates.repository":
        sys.modules.pop(_mod, None)
