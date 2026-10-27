### Create an Employee Schema  -- app/schemas/employee.py

### We will expose a simplified employee-creation endpoint.



from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # • This prevents users from submitting fields that are not defined in the model. If someone tries to pass an extra field (for example, age=30), Pydantic will raise a ValidationError. This is highly useful for keeping your API inputs strict and clean.

        str_strip_whitespace=True, # This automatically removes leading and trailing spaces from all string inputs before validating them.
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr = Field(
        max_length=254,
    )

    department: str = Field(
        min_length=2,
        max_length=100,
    )


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    notification_status: str


'''
The EmployeeCreate schema validates incoming employee data.

The EmployeeResponse schema defines the response structure.

For this training project, employee data will be stored in memory. It will not persist after the application restarts.

In a real Employee Management System, you would normally use SQLAlchemy and PostgreSQL.
'''
