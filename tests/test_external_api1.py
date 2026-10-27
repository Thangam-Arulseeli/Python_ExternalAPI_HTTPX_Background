###  Test Invalid External Responses    --- Add another test to tests/test_external_api.py.

import httpx
import pytest
from starlette.testclient import TestClient as TestClient  # noqa

from pydantic import ValidationError

from app.services.external_api_service import (
    ExternalAPIResponseError,
    ExternalAPIService,
)


@pytest.mark.asyncio
async def test_invalid_external_response():
    def mock_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "invalid",
                "name": None,
                "username": "Bret",
                "email": "not-an-email",
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(
        base_url="https://example.test",
        transport=transport,
    ) as client:
        service = ExternalAPIService(client)

        with pytest.raises(ExternalAPIResponseError):
            await service.get_user(1)


'''

This test confirms that an HTTP 200 response containing invalid data is not automatically accepted.

Why is this important?
``````````````````````
An upstream provider may return:

An unexpected response structure.
A string instead of an integer.
A missing required field.
An invalid email address.
HTML instead of JSON.
A successful HTTP status with an invalid payload.

Your backend should handle these conditions deliberately.

'''
