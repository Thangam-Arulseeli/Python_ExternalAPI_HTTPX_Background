### Streaming External API Responses with HTTPX

'''
We have implemented SSE output from FastAPI. Another related concept is streaming an external HTTP response through your backend.

HTTPX supports streaming responses without loading the entire body into memory.

Example Program:

'''

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse


router = APIRouter()


@router.get("/api/external/download")
async def download_external_file():
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=5.0,
            read=30.0,
            write=10.0,
            pool=5.0,
        )
    )

    try:
        upstream = await client.send(
            client.build_request(
                "GET",
                "https://example.com/large-file",
            ),
            stream=True,
        )

        upstream.raise_for_status()

    except httpx.HTTPError as exc:
        await client.aclose()

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve the external file.",
        ) from exc

    async def content_generator():
        try:
            async for chunk in upstream.aiter_bytes():
                yield chunk

        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(
        content_generator(),
        media_type=upstream.headers.get(
            "content-type",
            "application/octet-stream",
        ),
    )


'''

This example illustrates the streaming concept, but it is not the preferred implementation for the main training application.

It creates a new client for every download, forwards the response body without validating its contents, and does not handle every possible downstream-disconnect or upstream-error scenario.

In a production implementation:

Reuse a managed HTTPX client.
Stream the upstream response with correct resource cleanup.
Apply an appropriate total deadline.
Validate the upstream status and relevant headers.
Handle client disconnections.
Restrict which hosts and URLs may be accessed.
Avoid blindly forwarding security-sensitive headers.
Consider response size limits and content-disposition handling.

The key concept is that streaming avoids loading the complete response into memory before sending it to the client.

'''