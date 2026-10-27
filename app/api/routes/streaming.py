### Create the streaming route   --- Create app/api/routes/streaming.py

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse


router = APIRouter(
    prefix="/api/stream",
    tags=["Streaming"],
)


async def progress_event_generator():
    events = [
        {
            "status": "started",
            "progress": 0,
            "message": "Processing started",
        },
        {
            "status": "progress",
            "progress": 25,
            "message": "First stage completed",
        },
        {
            "status": "progress",
            "progress": 50,
            "message": "Second stage completed",
        },
        {
            "status": "progress",
            "progress": 75,
            "message": "Third stage completed",
        },
        {
            "status": "completed",
            "progress": 100,
            "message": "Processing completed",
        },
    ]

    for event in events:
        yield f"data: {json.dumps(event)}\n\n"

        await asyncio.sleep(2)


@router.get("/progress")
async def stream_progress():
    return StreamingResponse(
        progress_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )



'''
How does this work?
```````````````````````
StreamingResponse --> Sends response content incrementally rather than waiting to build one complete response body.

yield  --> Produces one chunk of response data at a time.

text/event-stream   -->  Specifies the SSE response content type.

\n\n    --> Separates individual SSE events.

X-Accel-Buffering: no   --> Requests that Nginx not buffer the response. Whether buffering is disabled depends on your reverse-proxy configuration.


Example event
data: {"status": "progress", "progress": 50, "message": "Second stage completed"}


Each event begins with data: and ends with a blank line.


How can a browser consume SSE?
`````````````````````````````````

For a public or cookie-authenticated endpoint, a browser can use:

const source = new EventSource(
    "http://localhost:8000/api/stream/progress"
);

source.onmessage = (event) => {
    const data = JSON.parse(event.data);

    console.log(data.status);
    console.log(data.progress);
    console.log(data.message);

    if (data.status === "completed") {
        source.close();
    }
};

source.onerror = () => {
    console.log("SSE connection encountered an error.");
};


Native browser EventSource does not provide a standard way to attach arbitrary authorization headers. For bearer-token authentication, consider a suitable fetch-based streaming client or another carefully designed authentication mechanism. Avoid putting long-lived secrets in query parameters.


Important SSE production considerations
``````````````````````````````````````````
For real applications, also consider:

Heartbeat events to keep idle connections alive.
Detecting client disconnects.
Reconnection behavior.
Event IDs and replay when required.
Reverse-proxy buffering and idle timeouts.
Authentication and authorization.
Limits on concurrent streaming connections.

Our example emits progress events from an in-memory sequence. It does not perform a real report-generation job.

For a production workflow, a durable background worker can process the job while a separate streaming endpoint reads its progress from a shared store.

'''