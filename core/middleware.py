"""
MinimalERP - Custom Middleware

Rate limiting, request logging, and other middleware components.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Callable
import redis.asyncio as redis
from core.config import settings

logger = logging.getLogger(__name__)

# Redis client for rate limiting
redis_client = None


async def get_redis_client():
    """Get or create Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.
    Limits requests per IP address.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""

        # Skip rate limiting for health check and metrics
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Get Redis client
        redis = await get_redis_client()

        # Create rate limit key
        key = f"rate_limit:{client_ip}"

        try:
            # Get current count
            current_count = await redis.get(key)

            if current_count is None:
                # First request from this IP
                await redis.setex(key, 60, 1)  # Expire in 60 seconds
            else:
                current_count = int(current_count)

                if current_count >= settings.RATE_LIMIT_PER_MINUTE:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Çok fazla istek gönderdiniz. Lütfen bir dakika bekleyin."
                    )

                # Increment counter
                await redis.incr(key)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            # Continue even if rate limiting fails

        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Request logging middleware.
    Logs all incoming requests with timing information.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging"""

        # Start timer
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Duration: {duration:.3f}s"
            )

            return response

        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"Exception: {str(e)} "
                f"Duration: {duration:.3f}s",
                exc_info=True
            )
            raise


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Audit log middleware for KVKK compliance.
    Logs all data access and modifications.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with audit logging"""

        # Skip audit for non-modifying requests
        if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return await call_next(request)

        # Get user from request (if authenticated)
        user_id = getattr(request.state, "user_id", None)

        # Log audit entry
        logger.info(
            f"Audit: User {user_id} "
            f"{request.method} {request.url.path}"
        )

        # TODO: Store audit log in database for KVKK compliance

        response = await call_next(request)
        return response
