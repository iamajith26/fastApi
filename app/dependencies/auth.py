from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.auth.jwt_handler import decode_access_token
import jwt
import logging

logger = logging.getLogger(__name__)

EXCLUDED_PATHS = ["/", "/auth/login", "/auth/register", "/auth/refresh_token", "/docs", "/openapi.json", "/redoc"]

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        # Get the token from the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]

        # Verify the token without database access
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if not user_id:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"message": "Invalid authentication credentials"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Access token has expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Invalid authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Add the user ID to the request state (no need to fetch full user here)
        request.state.user_id = user_id
        return await call_next(request)