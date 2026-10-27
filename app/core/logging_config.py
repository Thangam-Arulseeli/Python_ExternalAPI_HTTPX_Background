#### Logging Configuration   --- Create app/core/logging_config.py.

### Logging helps developers understand what happened when an external request fails.

import logging

from app.core.config import settings


logging.basicConfig(
    level=getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    ),
    format=(
        "%(asctime)s | " # The human-readable timestamp showing when the log record was created (e.g., 2026-10-27 08:18:00,123).
        "%(levelname)s | "  # The text severity level of the message (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        "%(name)s | "  # : The name of the logger (the logging channel) that issued the message, which typically corresponds to the module name like __name__.
        "%(message)s"  # %(message)s: The actual log message passed into the logging call (e.g., user logged in).
    ),
)


logger = logging.getLogger("external_api_app")


'''
Example:
-------------------
logger.info("External API request started")
logger.warning("External API returned HTTP 429")
logger.error("External API request failed")

In production, avoid logging API keys, authorization headers, passwords, or sensitive response bodies.
'''

