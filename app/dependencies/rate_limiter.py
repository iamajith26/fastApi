from fastapi import HTTPException, Header
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Redis configuration for rate limiting storage
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
    logger.info("Connected to Redis for rate limiting")
except:
    logger.warning("Redis not available, using in-memory rate limiting")
    redis_client = None

def get_user_identifier(request) -> str:
    """Get user identifier for rate limiting - prefer user ID over IP"""
    try:
        # Try to get user ID from request headers (set by gateway auth)
        user_id = request.headers.get("x-user-id")
        if user_id:
            return f"user:{user_id}"
    except:
        pass
    
    # Fallback to IP address
    return f"ip:{get_remote_address(request)}"

def get_authenticated_user_identifier(request) -> str:
    """Get user identifier for authenticated endpoints"""
    user_id = request.headers.get("x-user-id")
    if user_id:
        return f"auth_user:{user_id}"
    
    # For authenticated endpoints, still use IP as fallback
    return f"auth_ip:{get_remote_address(request)}"

# Create different limiters for different scenarios
if redis_client:
    # Use Redis for production
    limiter = Limiter(
        key_func=get_user_identifier,
        storage_uri=REDIS_URL,
        default_limits=["1000/hour"]  # Global default
    )
    
    auth_limiter = Limiter(
        key_func=get_authenticated_user_identifier,
        storage_uri=REDIS_URL,
        default_limits=["2000/hour"]  # Higher limit for authenticated users
    )
else:
    # Use in-memory for development
    limiter = Limiter(
        key_func=get_user_identifier,
        default_limits=["1000/hour"]
    )
    
    auth_limiter = Limiter(
        key_func=get_authenticated_user_identifier,
        default_limits=["2000/hour"]
    )

# Rate limiting configurations for different service types
RATE_LIMITS = {
    "auth": "10/minute",           # Authentication endpoints
    "users": "100/minute",         # User management
    "products": "200/minute",      # Product browsing (higher for catalog)
    "orders": "50/minute",         # Order operations (lower for security)
    "cart": "300/minute",          # Cart operations (highest for UX)
    "health": "60/minute",         # Health checks
    "public": "500/hour"           # Public endpoints per hour
}