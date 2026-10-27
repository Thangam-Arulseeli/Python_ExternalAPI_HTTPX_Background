###  Create the notification service   --- Create app/services/notification_service.py

import asyncio
import logging

logger = logging.getLogger(__name__)


async def send_welcome_notification(
    employee_id: int,
    employee_email: str,
) -> None:
    """
    Simulates sending an external notification.

    Replace this simulation with an actual email provider
    integration when connecting to a real service.
    """

    try:
        logger.info(
            "Preparing notification for employee %s",
            employee_id,
        )

        # Simulate asynchronous network I/O.
        await asyncio.sleep(2)

        logger.info(
            "Welcome notification sent to employee %s",
            employee_id,
        )

    except Exception:
        logger.exception(
            "Failed to send notification for employee %s",
            employee_id,
        )

        # This simple example logs the failure.
        # Production code may need a retry queue, alerting,
        # or a durable notification record.

'''
This example simulates a notification. It does not send an actual email.

An important design point is that an async def background function can perform asynchronous work. However, a blocking SMTP library or synchronous HTTP call inside it could still block the event loop.

Use an asynchronous client for asynchronous I/O, or appropriately offload unavoidable blocking work.
'''