Employee Management & External Services Integration API as our demo project
***********************************************************************************
What will we build?
====================
Suppose your company's Employee Management System needs to:

Fetch employee-related information from an external service.
Call multiple external APIs concurrently to reduce response time.
Authenticate with external APIs using API keys and custom headers.
Handle timeouts, network failures, retries, and rate limits.
Validate external API responses using Pydantic.
Send notifications in the background after an employee is created.
Stream progress updates to clients using Server-Sent Events (SSE).

We will implement these features using a modular, corporate-style project structure.

1. Session Roadmap
===========================
No.	Concept	                What you will learn
-------------------------------------------------------------------------------
1	External APIs	        API integration, request-response lifecycle
2	HTTPX	                Installing and using httpx
3	Async HTTP calls	    async, await, AsyncClient
4	API keys            	Secure authentication with external services
5	Headers	                Authorization, content type, custom headers
6	Timeouts	            Connect, read, write, and pool timeouts
7	Retries	                Retrying temporary failures safely
8	Response validation	    Validating external responses with Pydantic
9	Concurrent calls	    asyncio.gather() and structured concurrency concepts
10	Rate limits	            HTTP 429, Retry-After, backoff
11	BackgroundTasks	        Running small background    operations
12	Streaming and SSE	    Sending events incrementally
13	Error handling	        Mapping external API errors to appropriate HTTP responses
14	Testing	                Testing external API integration and background processing
15	Production practices	Logging, security, connection pooling, and job queues


Prerequisites
===============
You should already be familiar with:

Python functions, classes, exceptions, and type hints.
async and await.
FastAPI routes and dependency injection.
Pydantic schemas.
Environment variables and .env files.
Basic HTTP methods and status codes.

We will use FastAPI, HTTPX, Pydantic Settings, and pytest.



2. Understanding External APIs
==================================
2.1 What is an external API?

An external API is a service exposed by another application that your application can communicate with over a network.

For example, your Employee Management API may use:

External service	    Purpose
-----------------------------------------------------
Email API	            Send employee welcome emails
SMS API	                Send OTPs or notifications
Weather API	            Fetch location-based weather report
Payment API	            Process payments
HR API	                Fetch employee information
AI API	                Generate summaries or classifications



Consider this architecture:
=============================================
                  Employee Client
                         |
                         v
                 FastAPI Backend
                         |
                  Employee Service
                         |
              External API Service
                         |
                         v
                  HTTPX AsyncClient
                         |
                         v
                  External API
                         |
                         v
                   JSON Response
                         |
                         v
                Pydantic Validation
                         |
                         v
                   FastAPI Client

The important principle is that your business logic should not be tightly coupled to a particular external API.

For example, the employee service should not contain every detail about API authentication, URL construction, retry policies, and response parsing.

Instead, separate those responsibilities.


2.2 Understanding an HTTP request
=========================================
Suppose we want to fetch information from a public test API.

Request we send from the client
--------------------------------
Response will be given after processing the request [Response contains the Response Header and Response Body]

This is the basic request-response cycle.

The HTTP method describes the operation.
---------------------------------------
Method	        Purpose
--------------------------------------
GET	            Retrieve information
POST	        Create or submit information
PUT	            Replace a resource
PATCH	        Partially update a resource
DELETE	        Delete a resource

Important: A successful HTTP request does not automatically mean that the returned data is valid for your application.

NOTE: A response might contain unexpected fields, missing fields, or incorrect data types. That is why response validation is important.


3. What Is HTTPX?
=====================================
HTTPX is a Python HTTP client library used to send HTTP requests to other services.
It supports both synchronous and asynchronous requests.

 HTTPX is a next-generation, fully featured HTTP client for Python 3.9+ that provides both synchronous and asynchronous APIs. It builds upon the well-established usability of the popular requests library, making it largely compatible while adding modern features like HTTP/2 support, strict timeouts, and the ability to call WSGI/ASGI (Web Server Gateway Interface/ Asynchronous Server Gateway Interface. ) applications directly.


Key Features
```````````````
• Requests-Compatible API: If you know how to use requests, you already know how to use HTTPX.
• Async Support: Full support for asyncio and trio, allowing you to write high-performance concurrent code.
• HTTP/2 Support: Allows faster web requests via multiplexing.
• Connection Pooling: Automatically reuses TCP connections to reduce latency and resource overhead.
• Strict Timeouts: Unlike requests, HTTPX applies a default 5-second timeout everywhere to prevent hanging scripts.


NOTE:

Specification	Primary Execution Mode	        Best For	                    Popular Frameworks
---------------------------------------------------------------------------------------
WSGI	        Synchronous 	        Traditional HTTP APIs, CRUD apps,	   Flask,Django
                (Sequential request handling) and low-to-moderate traffic   (traditional)
                    t                                                                      
ASGI	  	Asynchronous    	            High-concurrency, WebSockets, 	        FastAPI, 
            (Concurrent, non-blocking handling)     real-time streaming      Django Channels



*** Synchronous HTTP request
----------------------------
import httpx

response = httpx.get(
    "https://jsonplaceholder.typicode.com/users/1"
)

print(response.status_code)
print(response.json())

This works, but the calling thread waits for the request to complete.


*** Asynchronous HTTP request
---------------------------------
import asyncio
import httpx


async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://jsonplaceholder.typicode.com/users/1"
        )

        print(response.status_code)
        print(response.json())


asyncio.run(main())

Here:

*   AsyncClient provides asynchronous HTTP operations.
*   await waits for the response without blocking the event loop while network I/O is pending.
*   asyncio.run() starts an event loop for this standalone example.


Inside FastAPI, you generally do not call asyncio.run() in an endpoint. 
FastAPI already runs asynchronous endpoints through its ASGI event loop.


Why use HTTPX with FastAPI?
=================================
Suppose your endpoint calls an external service that takes two seconds to respond.

A synchronous request made directly inside an async def endpoint can block the event loop.

An asynchronous HTTPX request allows the event loop to handle other work while waiting for the network response.

This improves concurrency for I/O-bound applications.

However, asynchronous code does not automatically make every operation faster. CPU-intensive calculations and blocking functions still require appropriate handling.


4. Complete Project Structure
=================================
We will organize the application using a layered architecture.

external_api_training/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── external.py
│   │       ├── employees.py
│   │       ├── background.py
│   │       └── streaming.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── external.py
│   │   └── employee.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── external_api_service.py
│   │   ├── employee_service.py
│   │   ├── notification_service.py
│   │   └── background_service.py
│   │
│   └── dependencies/
│       ├── __init__.py
│       └── http_client.py
│
└── tests/
    ├── __init__.py
    ├── test_external_api.py
    ├── test_employees.py
    └── test_background.py


Responsibilities of each layer
===================================
Layer	                Responsibility
------------------------------------------
api/routes/	            HTTP endpoints and request handling
core/config.py	        Environment-based configuration
core/logging_config.py	Application logging
schemas/	            Request and response validation
services/	            Business logic and external API integration
dependencies/	        Shared dependencies, including HTTP clients
tests/	                Automated tests

For this particular project, we do not need a database or repository layer because the demonstration focuses on external HTTP integrations and background processing.


NOTE: In your existing Employee Management application, you can add these components alongside your SQLAlchemy models, repositories, and database session.


5. Step 1 — Install the Required Packages
===============================================
Create a virtual environment.

    > python -m venv venv

Activate it on Windows:

    > .\venv\Scripts\Activate.ps1

Create requirements.txt.
```````````````````````````
fastapi
uvicorn[standard]
httpx
pydantic-settings
python-dotenv
pytest
pytest-asyncio


Install the packages:

    > python -m pip install -r requirements.txt

Verify HTTPX:

    > python -m pip show httpx


Training note: Use python -m pip rather than relying on the standalone pip command. This helps ensure that packages are installed into the active Python environment.

For a real project, pin tested dependency versions and maintain a lock file or equivalent reproducible dependency specification.


6. Step 2 — Environment Configuration
=========================================
External API configuration should not be scattered throughout the application.

Create .env.example:
```````````````````````
APP_NAME=External API Training Application

EXTERNAL_API_BASE_URL=https://jsonplaceholder.typicode.com
EXTERNAL_API_KEY=

EXTERNAL_API_TIMEOUT=5.0
EXTERNAL_API_MAX_RETRIES=2

LOG_LEVEL=INFO



Copy this file to .env.
```````````````````````````
In PowerShell:

    > Copy-Item .env.example .env

For this training example, the external API is public and does not require an API key.

We will still implement optional API-key support so that the same service structure can be adapted to authenticated APIs.


What is an environment variable?
===================================
An environment variable stores configuration outside your source code.

For example:

EXTERNAL_API_BASE_URL = "https://jsonplaceholder.typicode.com"

Hard-coding this value directly in multiple files makes changing environments more difficult.

----------------------------------

Instead, load it from configuration.

File: app/core/config.py


7. Step 3 — Logging Configuration
=======================================
Logging helps developers understand what happened when an external request fails.

Create app/core/logging_config.py.



Step 4 — Understand API Keys and HTTP Headers
=================================================

8.1 What is an API key?
```````````````````````````

An API key is a credential used by an external service to identify or authorize a client.

An external API might require:
````````````````````````````
GET /employees HTTP/1.1
Host: api.example.com
X-API-Key: your-api-key
Accept: application/json

The header name depends on the external provider.

Common patterns include:
--------------------------
Header	            Example	                    Purpose
````````````````````````````````````````````````````````````
X-API-Key	        X-API-Key: abc123	        API-key authentication
Authorization	    Bearer token123	            Token-based authentication
Accept	            application/json	        Expected response format
Content-Type	    application/json	        Request body format
X-Request-ID	    X-Request-ID: abc-123	    Request correlation

Do not assume that every provider accepts X-API-Key. Always follow the provider's documentation.



8.2 Construct headers safely
-----------------------------------
from app.core.config import settings


def build_external_api_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/json",
    }

    if settings.external_api_key:
        headers["X-API-Key"] = settings.external_api_key

    return headers


NOTE: Your backend keeps the credential private.

=====================================================


9. Step 5 — Define the External Response Schema
--------------------------------------------------

External services do not always return the data you expect.

Suppose our external service returns:

{
  "id": 1,
  "name": "Leanne Graham",
  "username": "Bret",
  "email": "Sincere@april.biz"
}


Create app/schemas/external.py.
`````````````````````````````````````

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class ExternalUser(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        strict=True,
    )

    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    username: str = Field(min_length=1)
    email: EmailStr


Because we use EmailStr, install its optional dependency:

    > python -m pip install email-validator


Add this package to requirements.txt:
```````````````````````````````````````
email-validator
````````````````
What does this schema validate?
`````````````````````````````````
Field	        Validation
id	            Must be an integer greater than zero
name	        Must be a nonempty string
username	    Must be a nonempty string
email	        Must be a valid email address

extra="ignore" means unexpected fields are ignored.

strict=True requests strict type validation, reducing implicit conversions.

For example, a string "1" will not automatically be accepted as an integer in strict validation.



Why validate external responses?
```````````````````````````````````````
Consider this unexpected response:

{
  "id": "invalid",
  "name": null,
  "email": "not-an-email"
}

If your application uses the response without validation, unexpected data can cause failures deeper in the business logic.

Pydantic lets you detect the problem near the integration boundary.

============================================================

10. Step 6 — Create a Reusable HTTPX Client Dependency
--------------------------------------------------------

This is an important design decision.

You could create a new AsyncClient for every API request, but repeatedly creating clients can prevent effective connection reuse.

Instead, create a client during application startup and close it during shutdown.


We will use FastAPI's lifespan mechanism.

Create app/dependencies/http_client.py.
`````````````````````````````````````````


11. Step 7 — Understand Timeouts
=======================================
Timeouts prevent requests from waiting indefinitely.

Imagine your FastAPI application calls an external email service.

The email service becomes unresponsive.

Without appropriate timeout settings, requests may occupy resources for longer than expected.

HTTPX supports separate timeout categories.
``````````````````````````````````````````````
Timeout	                Meaning
---------------------------------
Connect timeout	        Time allowed to establish a connection
Read timeout	        Maximum wait for incoming response data
Write timeout	        Maximum wait while sending request data
Pool timeout	        Maximum wait to obtain a connection from the pool

Example:

import httpx

timeout = httpx.Timeout(
    timeout=10.0,
    connect=2.0,
    read=5.0,
    write=5.0,
    pool=2.0,
)

Here, the default timeout is ten seconds, with the other values explicitly configured.

For example, a read timeout of five seconds means that HTTPX will not wait more than five seconds for the next chunk of response data.

It is not necessarily a five-second deadline for the entire request.

If you require an overall deadline, use an appropriate application-level deadline or cancellation strategy as well.

Common timeout error
````````````````````
except httpx.TimeoutException:
    ...

This catches HTTPX timeout exceptions, including connect, read, write, and pool timeouts.

A timeout does not always mean the external operation failed.

For example, if you submit a payment and time out waiting for the response, the payment might still have been processed.

This is why retries must be designed carefully
=========================================================


12. Step 8 — Implement the External API Service
=================================================
Now we will create the main integration service.

This service will handle:

External API requests.
API-key headers.
Retry logic.
Rate-limit responses.
Network errors.
Response validation.
Concurrent API requests.

Create app/services/external_api_service.py.
``````````````````````````````````````````````

NOTE:
RATE LIMITING
---------------
API rate limiting is a defensive technique used to restrict the number of requests a client can make to an API within a specified time period. When a user or application exceeds this threshold, the API rejects additional requests and typically returns an HTTP 429 Too Many Requests status code.

==================================================================================

13. Step 9 — Understanding the Retry Mechanism
-------------------------------------------------

A retry means attempting a failed operation again.

For example:

Attempt 1
    |
    v
External API returns 503 
    |
    v
Wait
    |
    v
Attempt 2
    |
    v
External API returns 503
    |
    v
Wait
    |
    v
Attempt 3
    |
    v
External API returns 200

In our configuration:

EXTERNAL_API_MAX_RETRIES=2


This means:
````````````
One initial attempt.
Up to two additional attempts.
Three total attempts at most.

NOTE: HTTP 503 Service Unavailable server error response status code indicates that the web server is operational, but it is currently not ready to handle the incoming request. This is typically a temporary condition(emporary, transient condition on the server side,) that will be resolved after some delay.


13.1 Exponential backoff
```````````````````````````
Exponential backoff increases the waiting time between attempts.

A simple formula is:

$$ \text{delay} = \min(\text{base} \times 2^{\text{attempt}}, \text{maximum}) $$

For example, with a one-second base:
```````````````````````````````````````
Retry attempt	        Delay before retry
````````````````````````````````````````````
First retry	            1 second
Second retry	        2 seconds
Third retry	            4 seconds
Fourth retry	        8 seconds

Our implementation also adds a small random delay, called jitter.

Jitter helps prevent many clients from retrying simultaneously after a service outage.


13.2 Which failures should be retried?
`````````````````````````````````````````````````````````````````````````
Failure     	        Usually retry?	            Reason
------------------------------------------------------------------------
Connection timeout	    Sometimes	                The network may recover
Connection failure	    Sometimes	                The failure may be temporary
HTTP 429	            Often	                    Respect provider rate-limit instructions
HTTP 500	            Sometimes	                Server-side failure may be temporary
HTTP 502	            Often	                    Temporary upstream failure
HTTP 503	            Often	                    Service may be temporarily unavailable
HTTP 504	            Often	                    Gateway timeout
HTTP 400	            Usually no	                Request is invalid
HTTP 401	            Usually no	                Authentication failed
HTTP 403	            Usually no	                Permission denied
HTTP 404	            Usually no	                Resource may not exist

These are defaults, not absolute rules. Provider-specific documentation and business semantics take precedence.

Critical production consideration: retry safety
```````````````````````````````````````````````````
The sample service retries GET requests.

GET is normally intended to be safe and idempotent (An idempotent operation is an action that can be applied multiple times without changing the result beyond the initial application.)

Be careful when retrying POST requests.

For example, if you submit a payment request and receive a timeout, the payment may have succeeded even though the response was lost.

Blindly repeating the POST could charge the customer twice.

For operations that support it, use idempotency keys and the provider's documented retry rules.

Another important consideration
``````````````````````````````````
Our example uses a simple retry loop. In production, consider the following:
--------------------------------------------------------------
A total request deadline.
A maximum acceptable Retry-After delay.
A shared rate limiter.
Circuit breakers for persistent outages.
Metrics for retries and failures.
Cancellation when the caller no longer needs the result.

Also, ensure that the retry policy does not multiply across multiple layers. If three layers each retry three times, one logical operation can generate many more upstream requests than expected.

=============================================================

14. Step 10 — Understanding Concurrent API Calls
----------------------------------------------------
Suppose your backend needs information about three users.

Sequential execution:

user1 = await service.get_user(1)
user2 = await service.get_user(2)
user3 = await service.get_user(3)

If each request takes approximately two seconds, total time may approach six seconds.

Concurrent execution:

users = await service.get_users_concurrently(
    [1, 2, 3]
)

If the requests take approximately two seconds each and run concurrently, the total time may be closer to two seconds, excluding overhead and retry delays.

Actual latency depends on network conditions, the provider, connection pooling, and resource limits.

14.1 What does asyncio.gather() do?
``````````````````````````````````````````
asyncio.gather() schedules multiple awaitable operations and waits for their results.

Example:

import asyncio

async def task(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} completed"

async def main():
    results = await asyncio.gather(
        task("Task A", 2),
        task("Task B", 2),
        task("Task C", 2),
    )

    print(results)

asyncio.run(main())
-------------------

The output is:

[
    'Task A completed',
    'Task B completed',
    'Task C completed'
]

The three simulated tasks take approximately two seconds together rather than six seconds sequentially.

The example uses asyncio.sleep() to simulate waiting; real HTTPX calls spend time waiting for network I/O.

Important limitation
``````````````````````````
By default, if one operation passed to asyncio.gather() raises an exception, the exception is propagated to the caller. The other operations are not automatically guaranteed to be cancelled and completed as one atomic unit.

If you need stronger structured-concurrency guarantees, consider asyncio.TaskGroup in Python 3.11 or later.

For independent external calls, you must decide what should happen when one fails:
`````````````````````````````````````````````````````````````````````````````````````
Fail the entire request.
Return successful results and individual failures.
Retry selected failures.
Cancel the remaining operations.

Our initial example uses the simplest policy: if any call fails, the overall operation fails.

14.2 Why concurrency needs limits
`````````````````````````````````````
Suppose a client requests 1,000 external API calls simultaneously.

Unrestricted concurrency can:
`````````````````````````````````
Exhaust connection-pool capacity.
Overload the external provider.
Trigger HTTP 429 responses.
Increase memory usage.
Increase failure rates.

For production applications, use bounded concurrency, per-provider limits, and batch-size restrictions.

The sample endpoint below limits each request to 20 user IDs. A production service should additionally consider a shared semaphore or rate limiter across incoming requests.

========================================================================

15. Step 11 — Create an Employee Schema
----------------------------------------------
We will expose a simplified employee-creation endpoint.

Create app/schemas/employee.py.

=================================================================

16. Step 12 — Create the Employee Service
`````````````````````````````````````````````
Create app/services/employee_service.py.

================================================================


17. Step 13 — Background Processing with FastAPI
================================================
17.1 What is background processing?
``````````````````````````````````````
Background processing means executing work outside the main response-generation path.


Suppose an employee is created.

The application may need to:
```````````````````````
Validate the employee information.
Save the employee.
Return a successful response.
Send a welcome notification.

The notification does not necessarily need to complete before the HTTP response is returned.

A simple flow is:

Client
  |
  v
POST /api/employees
  |
  v
Validate Employee
  |
  v
Save Employee
  |
  v
Schedule Notification
  |
  v
Return HTTP Response
  |
  v
Execute Background Task
  |
  v
Send Notification

FastAPI provides BackgroundTasks for small tasks associated with a response.


17.2 Create the notification service
``````````````````````````````````````````
Create app/services/notification_service.py.

================================================================
17.3 Create a background processing service
`````````````````````````````````````````````````
Create app/services/background_service.py.

====================================================

18. Step 14 — Create the External API Routes
```````````````````````````````````````````````
Create app/api/routes/external.py.

===============================================

19. Step 15 — Create the Employee Routes with BackgroundTasks
-------------------------------------------------------

Create app/api/routes/employees.py.

=========================================


20. Step 16 — Understanding HTTP 429 and Rate Limiting
--------------------------------------------------------------
Rate limiting controls how many requests a client may send during a given period.

For example, a provider might allow:

100 requests per minute per API key

If your application exceeds that limit, the provider may respond:

HTTP/1.1 429 Too Many Requests

This tells the client that the request was rate-limited and suggests waiting ten seconds before retrying.

NOTE:
------
The HTTP 429 Too Many Requests client error response status code indicates that the client has sent too many requests to the server in a given amount of time. This mechanism is universally referred to as rate limiting and acts as traffic control to protect server resources from being overloaded, abused, or targeted by DDoS attacks.

20.1 Important rate-limit headers (Key Features of a 429 Response)
``````````````````````````````````````````````
Header	                    Purpose
````````````````````````````````````````````````````````````
Retry-After	                Suggested time to wait in seconds

Rate-Limit Intelligence: Many modern APIs provide diagnostic headers
---------------------
X-RateLimit-Limit       	Maximum request count, if provided
X-RateLimit-Remaining   	Remaining quota, if provided
X-RateLimit-Reset	        Quota reset time, if provided (time when the window resets)

The X-RateLimit-* headers are provider-specific conventions rather than universal HTTP requirements.


How our service handles HTTP 429
``````````````````````````````````
The earlier service:

Detects status code 429.
Reads the Retry-After header.
Uses exponential backoff when no valid delay is available.
Adds jitter.
Retries within the configured retry limit.
Returns a controlled exception if the limit is still exceeded.


Why shouldn't we retry indefinitely?
`````````````````````````````````````````
Imagine your service receives 100 requests per second.

Every request calls the same provider, which permits only 20 requests per second.

Unrestricted retries will generate more traffic, making the problem worse.

Instead, consider:
```````````````````````
Per-provider rate limits.
Shared request quotas.
Concurrency limits.
Queue-based processing.
Circuit breakers.
Request coalescing or caching.
Retry budgets.


Important production detail: A retry loop inside each incoming request is not a global rate limiter. If 50 incoming requests each create their own retry loop, they can still overwhelm the external provider.

A shared limiter must coordinate requests across the relevant application workers or instances.

=====================================================


21. Step 17 — Implement an SSE Streaming Endpoint
--------------------------------------------------------

21.1 What is Server-Sent Events?
``````````````````````````````````
Server-Sent Events (SSE) allow a server to send a continuous stream of events to a client over an HTTP connection.

For example, a report-generation endpoint could stream progress updates:

Connection established
        |
        v
Event: started
Data: Report generation started
        |
        v
Event: progress
Data: 25% complete
        |
        v
Event: progress
Data: 50% complete
        |
        v
Event: progress
Data: 100% complete
        |
        v
Event: completed
Data: Report generation completed


NOTE:
SSE is useful when the server needs to send updates to the client without requiring the client to repeatedly poll an endpoint.

Typical use cases include:
```````````````````````````````
Long-running report progress.
AI-generated text or status updates.
Notification streams.
Live processing logs.
Dashboard status updates.

SSE is one-way: the server sends events to the client. For bidirectional communication, WebSockets may be more suitable.


21.2 Create the streaming route
```````````````````````````````````
Create app/api/routes/streaming.py.

-------------------------------------

=================================================================


22. Step 18 — Complete the Main FastAPI Application
-----------------------------------------------------

Create app/main.py.

====================================================================


23. Step 19 — Create the Package Initialization Files
------------------------------------------------------------
Create empty files:

app/__init__.py
app/api/__init__.py
app/api/routes/__init__.py
app/core/__init__.py
app/schemas/__init__.py
app/services/__init__.py
app/dependencies/__init__.py
tests/__init__.py


These files help establish Python package boundaries.

Modern Python can also support namespace packages without every __init__.py file, but this explicit structure is easy to understand during training.

============================================================


24. Step 20 — Run the Application
-------------------------------------
From the project root:

    > uvicorn app.main:app --reload

If the uvicorn command is not recognized:

    > python -m uvicorn app.main:app --reload

Open Swagger UI:

    http://127.0.0.1:8000/docs

Open ReDoc:

    http://127.0.0.1:8000/redoc


The main API endpoints are as follows:
```````````````````````````````````````````
Method	    Endpoint	                            Purpose
``````````````````````````````````````````````````````````````````````````
GET	        /	                                    Application information
GET	        /health	                                Health status
GET	        /api/external/users/1	                Fetch one external user
GET	        /api/external/users?ids=1&ids=2	        Fetch multiple users concurrently
POST	    /api/employees	                Create employee and schedule notification
GET	        /api/employees/1	        Retrieve an employee from the in-memory store
GET	        /api/stream/progress	                Stream progress using SSE


=========================================================================


25. Step 21 — Test External API Calls in Swagger
----------------------------------------------------
Test 1: Fetch one external user
`````````````````````````````````
Endpoint:

GET /api/external/users/1

Expected response:

{
  "id": 1,
  "name": "Leanne Graham",
  "username": "Bret",
  "email": "Sincere@april.biz"
}

This request goes to the JSONPlaceholder test API.
External network access is required.
If the external service is unavailable, your application may return a controlled error instead.


Test 2: Fetch multiple users concurrently
```````````````````````````````````````````````
Endpoint:

GET /api/external/users?ids=1&ids=2&ids=3

Expected structure:

{
  "count": 3,
  "users": [
    {
      "id": 1,
      "name": "Leanne Graham",
      "username": "Bret",
      "email": "Sincere@april.biz"
    },
    {
      "id": 2,
      "name": "Ervin Howell",
      "username": "Antonette",
      "email": "Shanna@melissa.tv"
    },
    {
      "id": 3,
      "name": "Clementine Bauch",
      "username": "Samantha",
      "email": "Nathan.McCullough@kory.org"
    }
  ]
}

The endpoint fetches all requested users concurrently.
Actual results depend on the external service and network availability.


Test 3: Create an employee
`````````````````````````````
Endpoint:

POST /api/employees

Request body:

{
  "name": "Arun Kumar",
  "email": "arun@example.com",
  "department": "Engineering"
}

Expected response:

{
  "id": 1,
  "name": "Arun Kumar",
  "email": "arun@example.com",
  "department": "Engineering",
  "notification_status": "scheduled"
}

The response indicates that the notification task has been scheduled.
The example does not send an actual email.



Test 4: Stream progress
`````````````````````````
Open:

http://127.0.0.1:8000/api/stream/progress

The response should display SSE data as it arrives, depending on the browser or client used.

For a more explicit command-line test, use:

curl.exe -N http://127.0.0.1:8000/api/stream/progress

The -N option disables curl's output buffering so the events can be observed incrementally.


==================================================================================


26. Step 22 — Testing the Integration with pytest
------------------------------------------------------
A corporate training project should not rely only on Swagger testing.

We should also test the service independently of the real external API.

This is especially important because external API tests can fail due to:
``````````````````````````````
Network outages.
DNS problems.
Provider downtime.
Rate limits.
Changes in test-service behavior.

HTTPX provides MockTransport, which allows you to simulate HTTP responses without making real network requests.

Create tests/test_external_api.py
.......
.......


Run:

    > python -m pytest -v


What does this test prove?
````````````````````````````
It verifies that:
```````
The service requests the expected path.
The mock external service returns JSON.
Pydantic validates the JSON.
The service returns a typed ExternalUser instance.

It does not depend on the availability of a real external API.


27. Step 23 — Test Invalid External Responses
`````````````````````````````````````````````````
Add another test to tests/test_external_api1.py.
.....
.....


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

==================================================


28. Step 24 — Test Employee Creation and BackgroundTasks
--------------------------------------------------------

Create tests/test_employees.py.

==========================================================

29. Step 25 — Understanding the Main Error Types
````````````````````````````````````````````````
HTTPX exposes different exceptions for different kinds of failures.

Exception	            Meaning	                                    Typical handling
httpx.TimeoutException	An HTTP operation timed out	                Consider a bounded retry
httpx.ConnectError	    Connection establishment failed	            Consider a retry
httpx.ReadError	        Error while reading response data	Consider provider-specific handling
httpx.WriteError	    Error while sending request data	Be careful when retrying writes
httpx.PoolTimeout	    No connection became available within the pool timeout	Review concurrency and pool sizing
httpx.HTTPStatusError	An error status was raised by raise_for_status()	Map the failure appropriately
httpx.RequestError	    Base class for request-related errors	Catch when broader network handling is appropriate


The precise exception hierarchy matters.

For example, PoolTimeout is a timeout exception, so our retry loop treats it as a timeout. But repeated pool timeouts may indicate local overload rather than an upstream outage.

Blindly retrying a pool timeout can make local contention worse.

Similarly, HTTP 401 and 403 should not be retried automatically unless there is a specific credential-refresh or authorization-recovery mechanism.

========================================================================