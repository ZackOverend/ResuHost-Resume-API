import logging
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


def error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": request.state.request_id,
    }
    if details is not None:
        error["details"] = details
    return JSONResponse({"error": error}, status_code=status_code)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, str):
            message = detail
        elif isinstance(detail, dict) and isinstance(detail.get("message"), str):
            message = detail["message"]
        else:
            message = "Request failed"
        return error_response(
            request,
            status_code=exc.status_code,
            code=f"http_{exc.status_code}",
            message=message,
            details=None if isinstance(detail, str) else detail,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            request,
            status_code=422,
            code="validation_error",
            message="Request validation failed",
            details=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled request error",
            extra={"request_id": request.state.request_id},
        )
        return error_response(
            request,
            status_code=500,
            code="internal_error",
            message="An unexpected error occurred",
        )


def request_id_from(request: Request) -> str:
    supplied = request.headers.get("X-Request-ID", "").strip()
    return supplied[:128] if supplied else str(uuid4())
