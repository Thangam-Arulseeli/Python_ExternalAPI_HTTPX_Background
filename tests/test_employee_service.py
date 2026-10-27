from fastapi.testclient import TestClient
from starlette.testclient import TestClient as TestClient  # noqa

from app.main import app


def test_create_employee():
    with TestClient(app) as client:
        response = client.post(
            "/api/employees",
            json={
                "name": "Arun Kumar",
                "email": "arun@example.com",
                "department": "Engineering",
            },
        )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "Arun Kumar"
    assert body["email"] == "arun@example.com"
    assert body["department"] == "Engineering"
    assert body["notification_status"] == "scheduled"



'''
Run:

python -m pytest -v

A subtle testing detail
````````````````````````
FastAPI's TestClient normally waits for background tasks associated with the request to finish before the test call completes.

Therefore, the test above may wait for the two-second notification simulation.

That is useful when testing the complete request lifecycle, but it is not always ideal for every test.

For more focused tests, you can mock the notification function or test the notification service independently.

'''

