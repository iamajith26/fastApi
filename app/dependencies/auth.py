from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.db.session import get_db
from app.auth.jwt_handler import verify_jwt_token
from sqlalchemy.orm import Session
import jwt  # Add this import

EXCLUDED_PATHS = ["/", "/auth/login", "/auth/register", "/auth/refresh_token"]

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

        # Verify the token
        db: Session = get_db().__next__()  # Get a database session
        user = None
        try:
            user = verify_jwt_token(token, db)
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

        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Invalid authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Add the user to the request state
        request.state.user = user
        return await call_next(request)