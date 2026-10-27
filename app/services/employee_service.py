### Create the Employee Service     ---   app/services/employee_service.py

from itertools import count

from app.schemas.employee import EmployeeCreate


class EmployeeService:
    def __init__(self) -> None:
        self._employees: dict[int, dict] = {}
        self._counter = count(1)

    def create_employee(
        self,
        data: EmployeeCreate,
    ) -> dict:
        employee_id = next(self._counter)

        employee = {
            "id": employee_id,
            "name": data.name,
            "email": str(data.email),
            "department": data.department,
        }

        self._employees[employee_id] = employee

        return employee

    def get_employee(
        self,
        employee_id: int,
    ) -> dict | None:
        return self._employees.get(employee_id)


    '''
This is intentionally a lightweight implementation.

Production warning: A module-level in-memory store is not a substitute for a database. Multiple workers maintain separate memory, data disappears on restart, and concurrent updates require additional care.

For a real employee application, persist employee data through your SQLAlchemy repository and database session.
    '''