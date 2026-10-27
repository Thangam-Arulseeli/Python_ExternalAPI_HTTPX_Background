### Create a background processing service   --- app/services/background_service.py

import logging

from app.services.notification_service import (
    send_welcome_notification,
)

logger = logging.getLogger(__name__)


async def process_employee_notification(
    employee_id: int,
    employee_email: str,
) -> None:
    logger.info(
        "Background notification started for employee %s",
        employee_id,
    )

    await send_welcome_notification(
        employee_id=employee_id,
        employee_email=employee_email,
    )

    logger.info(
        "Background notification processing finished for employee %s",
        employee_id,
    )


    '''
This extra service layer is optional for such a small example, but it demonstrates how to separate background orchestration from individual notification operations.


What does this background task guarantee?
`````````````````````````````````````
It does not guarantee durable execution.

If the application process crashes, a queued in-process background task may be lost.

For reliable delivery, use a durable queue or job system, such as Celery with a message broker, or a comparable platform.
    
    '''
