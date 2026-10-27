### Create the Employee Routes with BackgroundTasks   -- Create app/api/routes/employees.py

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
)

from app.services.employee_service import EmployeeService

from app.services.background_service import (
    process_employee_notification,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"],
)

employee_service = EmployeeService()


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=201,
)
async def create_employee(
    employee: EmployeeCreate,
    background_tasks: BackgroundTasks,
):
    created_employee = employee_service.create_employee(
        employee
    )

    background_tasks.add_task(
        process_employee_notification,
        created_employee["id"],
        created_employee["email"],
    )

    logger.info(
        "Employee %s created; notification scheduled",
        created_employee["id"],
    )

    return {
        **created_employee,
        "notification_status": "scheduled",
    }


@router.get("/{employee_id}")
async def get_employee(
    employee_id: int,
):
    employee = employee_service.get_employee(
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found.",
        )

    return employee


'''
What does background_tasks.add_task() do?
````````````````````````````````````````````

It registers a callable to execute after the response has been sent.

For example:

background_tasks.add_task(
    process_employee_notification,
    employee_id,
    employee_email,
)

The arguments are passed to the function when FastAPI executes the task.

The endpoint returns:

{
  "id": 1,
  "name": "Arun Kumar",
  "email": "arun@example.com",
  "department": "Engineering",
  "notification_status": "scheduled"
}

The notification task then runs in the background.

Notice that "scheduled" does not mean that the email has been delivered. It means only that the application scheduled the work.



When should you use BackgroundTasks?
```````````````````````````````````````
Good examples include:

Writing noncritical audit information.
Sending simple notifications.
Performing small follow-up operations.
Triggering lightweight post-response processing.

Avoid using it as a substitute for a durable job queue for:

Large reports.
Long-running data processing.
High-volume email campaigns.
Tasks requiring guaranteed delivery.
Jobs that need persistence, distributed workers, or advanced retries.

Also, BackgroundTasks does not create a separate distributed worker. It is an in-process mechanism associated with the response.

'''


