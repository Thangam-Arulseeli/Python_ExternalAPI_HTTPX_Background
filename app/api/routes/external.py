### Create the External API Routes  --- Create app/api/routes/external.py

import asyncio

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.services.external_api_service import (
    ExternalAPIError,
    ExternalAPIResponseError,
    ExternalAPIRateLimitError,
    ExternalAPITimeoutError,
    ExternalAPIUnavailableError,
    ExternalAPIService,
)


router = APIRouter(
    prefix="/api/external",
    tags=["External APIs"],
)


class ExternalUsersResponse(BaseModel):
    users: list[dict]


def get_service(request: Request) -> ExternalAPIService:
    return ExternalAPIService(request.app.state.http_client)


@router.get("/users/{user_id}")
async def get_external_user(
    user_id: int,
    request: Request,
):
    if user_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="User ID must be greater than zero.",
        )

    service = get_service(request)

    try:
        user = await service.get_user(user_id)
        return user

    except ExternalAPITimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="The external service timed out.",
        ) from exc

    except ExternalAPIRateLimitError as exc:
        raise HTTPException(
            status_code=503,
            detail="The external service is rate-limiting requests.",
            headers={"Retry-After": "5"},
        ) from exc

    except ExternalAPIUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail="The external service is temporarily unavailable.",
        ) from exc

    except ExternalAPIResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail="The external service returned invalid data.",
        ) from exc

    except ExternalAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail="An external API error occurred.",
        ) from exc



@router.get("/users")
async def get_multiple_users(
    request: Request,
    ids: list[int] = Query(
        ...,
        min_length=1,
        max_length=20,
    ),
):
    if any(user_id <= 0 for user_id in ids):
        raise HTTPException(
            status_code=422,
            detail="All user IDs must be greater than zero.",
        )

    service = get_service(request)

    try:
        users = await service.get_users_concurrently(ids)

        return {
            "count": len(users),
            "users": users,
        }

    except ExternalAPITimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="An external API request timed out.",
        ) from exc

    except ExternalAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve external users.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


    '''
    What happens when the endpoint is called?

Example:

GET /api/external/users/1

The request passes through these steps:

FastAPI validates user_id.
The route retrieves the shared HTTPX client.
The route constructs the external API service.
The service calls the external API.
The service retries eligible temporary failures.
The response is validated with Pydantic.
FastAPI returns the result.
Understanding HTTP 502 versus 504
Status code	Meaning
502 Bad Gateway	An upstream service returned an invalid or unusable response
503 Service Unavailable	The service is temporarily unavailable
504 Gateway Timeout	The upstream service did not respond in time

These status codes are useful for communicating failures in a service that depends on another service.

The route should not expose raw exception messages, internal URLs, credentials, or stack traces to clients.

Implementation note: The current service intentionally retries only GET requests and handles expected HTTPX failures. A larger application should centralize error mapping rather than duplicating it across many route handlers.
    '''
