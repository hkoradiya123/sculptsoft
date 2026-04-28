from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from app.utils.logger import logger

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except RateLimitExceeded:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get user info if available
        user_info = "Anonymous"
        if hasattr(request.state, "user"):
            user_info = request.state.user.email
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            f"Path: {request.url.path} | Method: {request.method} | "
            f"Status: {response.status_code} | User: {user_info} | "
            f"Duration: {process_time:.3f}s"
        )
        
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response
