import httpx
import pytest
from starlette.testclient import TestClient as TestClient  # noqa

from app.services.external_api_service import (
    ExternalAPIService,
)


@pytest.mark.asyncio
async def test_get_user_success():
    def mock_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        assert request.url.path == "/users/1"

        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Leanne Graham",
                "username": "Bret",
                "email": "Sincere@april.biz",
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(
        base_url="https://example.test",
        transport=transport,
    ) as client:
        service = ExternalAPIService(client)

        user = await service.get_user(1)

    assert user.id == 1
    assert user.name == "Leanne Graham"
    assert str(user.email) == "Sincere@april.biz"



    '''
Run:

    > python -m pytest -v


What does this test prove?

It verifies that:

The service requests the expected path.
The mock external service returns JSON.
Pydantic validates the JSON.
The service returns a typed ExternalUser instance.

It does not depend on the availability of a real external API.
    
'''