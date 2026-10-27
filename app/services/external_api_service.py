#### Implement the External API Service  -- app/services/external_api_service.py.

'''
Now we will create the main integration service.

This service will handle:

External API requests.
API-key headers.
Retry logic.
Rate-limit responses.
Network errors.
Response validation.
Concurrent API requests.

'''

import asyncio
import random
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Any

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.external import ExternalUser


class ExternalAPIError(Exception):
    """Base exception for external API failures."""


class ExternalAPITimeoutError(ExternalAPIError):
    """The external API did not respond within the timeout."""


class ExternalAPIRateLimitError(ExternalAPIError):
    """The external API rate limit was exceeded."""


class ExternalAPIUnavailableError(ExternalAPIError):
    """The external API is temporarily unavailable."""


class ExternalAPIResponseError(ExternalAPIError):
    """The external API returned an invalid response."""


class ExternalAPIService:
    def __init__(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        self.client = client

    def _build_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
        }

        if settings.external_api_key:
            headers["X-API-Key"] = settings.external_api_key

        return headers


    @staticmethod
    def _retry_after_seconds(
        response: httpx.Response,
    ) -> float | None:
        value = response.headers.get("Retry-After")

        if not value:
            return None

        # Retry-After can be a number of seconds.
        try:
            seconds = float(value)

            if seconds >= 0:
                return seconds

            return None
        except ValueError:
            pass

        # It can also be an HTTP date.
        try:
            retry_at = parsedate_to_datetime(value)

            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(
                    tzinfo=timezone.utc
                )

            seconds = (
                retry_at - datetime.now(timezone.utc)
            ).total_seconds()

            return max(0.0, seconds)

        except (TypeError, ValueError, OverflowError):
            return None


    async def _get_with_retry(
        self,
        path: str,
    ) -> httpx.Response:
        max_retries = settings.external_api_max_retries

        for attempt in range(max_retries + 1):
            try:
                response = await self.client.get(
                    path,
                    headers=self._build_headers(),
                )

            except httpx.TimeoutException as exc:
                logger.warning(
                    "External API timeout on attempt %s",
                    attempt + 1,
                )

                if attempt == max_retries:
                    raise ExternalAPITimeoutError(
                        "The external API timed out."
                    ) from exc

                delay = min(2**attempt, 8)
                delay += random.uniform(0, 0.25) # • it will pick a random fraction of a second, between 0 and 0.25 [such as 0.041, 0.187, or 0.233]. 


                await asyncio.sleep(delay)
                continue

            except httpx.RequestError as exc:
                logger.warning(
                    "External API network failure on attempt %s",
                    attempt + 1,
                )

                if attempt == max_retries:
                    raise ExternalAPIUnavailableError(
                        "The external API is unavailable."
                    ) from exc

                delay = min(2**attempt, 8)
                delay += random.uniform(0, 0.25)

                await asyncio.sleep(delay)
                continue

            if response.status_code == 429:  #  HTTP 429 Too Many Requests
                retry_after = self._retry_after_seconds(
                    response
                )

                if attempt == max_retries:
                    raise ExternalAPIRateLimitError(
                        "The external API rate limit was exceeded."
                    )

                delay = min(2**attempt, 8)

                if retry_after is not None:
                    # Do not retry earlier than requested.
                    # Avoid excessive sleeping in this example.
                    if retry_after > 10:
                        raise ExternalAPIRateLimitError(
                            "The external API requested a long retry delay."
                        )

                    delay = max(delay, retry_after)

                delay += random.uniform(0, 0.25)

                await asyncio.sleep(delay)
                continue

            if response.status_code in (408, 500, 502, 503, 504): # 408 Request Timeout
                if attempt == max_retries:
                    response.raise_for_status()

                delay = min(2**attempt, 8)
                delay += random.uniform(0, 0.25)

                await asyncio.sleep(delay)
                continue

            # Other 4xx errors usually indicate a problem with
            # the request, credentials, or permissions.
            # Do not retry them automatically.
            response.raise_for_status()

            return response

        raise ExternalAPIUnavailableError(
            "The external API request could not be completed."
        )


    async def get_user(
        self,
        user_id: int,
    ) -> ExternalUser:
        response = await self._get_with_retry(
            f"/users/{user_id}"
        )

        try:
            payload: Any = response.json()

            return ExternalUser.model_validate(payload)

        except (ValueError, ValidationError) as exc:
            raise ExternalAPIResponseError(
                "The external API returned invalid user data."
            ) from exc

    async def get_users_concurrently(
        self,
        user_ids: list[int],
    ) -> list[ExternalUser]:
        if len(user_ids) > 20:
            raise ValueError(
                "A maximum of 20 users can be fetched per request."
            )

        results = await asyncio.gather(
            *[
                self.get_user(user_id)
                for user_id in user_ids
            ]
        )

        return results

    '''
This service provides a substantial starting point for training.

However, before treating it as production-ready, understand the design decisions and limitations below.
    '''