"""FastAPI middleware: CORS, response-size guard."""
from __future__ import annotations

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from alias_core.config.settings import settings


def add_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class ResponseSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject responses larger than MAX_RESPONSE_SIZE bytes."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > settings.max_response_size:
            return Response(
                content='{"error": "Response too large"}',
                status_code=413,
                media_type="application/json",
            )
        return response


def add_middleware(app: FastAPI) -> None:
    add_cors(app)
    app.add_middleware(ResponseSizeLimitMiddleware)
