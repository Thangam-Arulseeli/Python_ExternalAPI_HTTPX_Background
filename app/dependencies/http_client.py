### 10. Step 6 — Create a Reusable HTTPX Client Dependency

'''
This is an important design decision.

You could create a new AsyncClient for every API request, but repeatedly creating clients can prevent effective connection reuse.

Instead, create a client during application startup and close it during shutdown.

We will use FastAPI's lifespan mechanism.

'''

import httpx

from app.core.config import settings


def create_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.external_api_base_url,
        timeout=httpx.Timeout(
            timeout=settings.external_api_timeout,  # timeout (settings.external_api_timeout): The fallback or default timeout applied to any of the four phases below if they are not explicitly overridden, or the overall safety ceiling depending on how HTTPX handles global defaults.
            connect=2.0, # he maximum time allowed to establish a socket connection to the remote server [ConnectTimeout]
            read=5.0, # The maximum time allowed to wait between consecutive chunks of data received from the server while reading the response.[ReadTimeout ]
            write=5.0, # he maximum time allowed to send the request body (upload data) to the server. [WriteTimeout ]
            pool=2.0, # The maximum time allowed to wait for an available connection slot from the internal connection pool [PoolTimeout]
        ),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=30.0,
        ),
        follow_redirects=False,
        headers={
            "Accept": "application/json",
            "User-Agent": "EmployeeManagementAPI/1.0",
        },
    )


'''
Understanding the configuration
==================================

base_url  --> Defines the default host for requests.

Instead of:

await client.get(
    "https://jsonplaceholder.typicode.com/users/1"
)


you can write:  --> await client.get("/users/1")

timeout   -->  Defines how long HTTP operations can wait before timing out.

limits   --> Controls the client's connection pool.

max_connections=100   -->  Allows up to 100 simultaneous connections in the configured pool. This is a resource limit, not a promise that the external provider can handle 100 requests at once.

max_keepalive_connections=20   -->  Controls how many idle connections can be retained for reuse.

keepalive_expiry=30.0   --> Sets the idle keep-alive expiration period in seconds.

These settings are starting points for training, not universal production values. Tune them according to traffic, latency, provider limits, and deployment resources.

'''