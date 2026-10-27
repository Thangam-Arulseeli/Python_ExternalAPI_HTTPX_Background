### Complete the Main FastAPI Application -- Create app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import (
    external,
    employees,
    streaming,
)

from app.core.config import settings
from app.core.logging_config import logger

from app.dependencies.http_client import (
    create_http_client,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")

    app.state.http_client = create_http_client()

    try:
        yield

    finally:
        await app.state.http_client.aclose()

        logger.info("Application shutdown completed")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Training application demonstrating external APIs, "
        "HTTPX, asynchronous requests, background processing, "
        "and SSE."
    ),
    lifespan=lifespan,
)


app.include_router(external.router)
app.include_router(employees.router)
app.include_router(streaming.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "application": settings.app_name,
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
    }


'''
What is lifespan?
``````````````````````````
The lifespan function manages application startup and shutdown.


During startup:
````````````````
app.state.http_client = create_http_client()

A reusable HTTPX client is created.


During shutdown:
``````````````````
await app.state.http_client.aclose()

The HTTP client is closed and its resources are released.

This is preferable to creating a new HTTP client for every individual external request.


Deployment consideration: Each application worker has its own process and therefore its own HTTP client and connection pool. Pool limits are not automatically shared across workers.

'''