"""
Error Handling Middleware
Custom exception handlers and middleware for better error responses
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
from config.logging_config import get_logger

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions with standardized format
    
    Args:
        request: FastAPI request
        exc: HTTP exception
        
    Returns:
        JSON response with error details
    """
    logger.warning(
        f"HTTP {exc.status_code} - {request.method} {request.url.path} - {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors with detailed information
    
    Args:
        request: FastAPI request
        exc: Validation error
        
    Returns:
        JSON response with validation error details
    """
    errors = exc.errors()
    logger.warning(
        f"Validation Error - {request.method} {request.url.path} - {len(errors)} error(s)"
    )
    
    # Format validation errors
    formatted_errors = []
    for error in errors:
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "detail": "Request validation failed",
            "status_code": 422,
            "validation_errors": formatted_errors
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions with logging
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON response with error details
    """
    logger.error(
        f"Unhandled Exception - {request.method} {request.url.path} - {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.__class__.__name__,
            "detail": "Internal server error occurred",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )


class RequestLoggingMiddleware:
    """
    Middleware to log all requests and responses
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # Extract request info
        method = scope["method"]
        path = scope["path"]
        client = scope.get("client", ["unknown", 0])
        client_ip = client[0] if client else "unknown"
        
        # Log request
        logger.info(f"→ {method} {path} from {client_ip}")
        
        # Track response
        status_code = 500
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Log response
            duration_ms = int((time.time() - start_time) * 1000)
            log_level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
            getattr(logger, log_level)(
                f"← {method} {path} - {status_code} ({duration_ms}ms)"
            )
