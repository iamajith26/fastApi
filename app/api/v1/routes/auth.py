from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.schemas.user import UserCreate, RegistrationMessage, LoginRequest
from app.services.auth_service import AuthService, get_auth_service
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_refresh_token
from app.dependencies.rate_limiter import limiter, RATE_LIMITS
import jwt
from app.schemas.token import RefreshTokenRequest
from fastapi.responses import JSONResponse
from fastapi import Header

router = APIRouter()

@router.post("/register", response_model=RegistrationMessage, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Strict limit for registration
async def register_user(request: Request, user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.register_user(user)

@router.post("/login")
@limiter.limit(RATE_LIMITS["auth"])  # 10/minute for login attempts
async def login_user(request: Request, credentials: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    user_db = await auth_service.authenticate_user(credentials.email, credentials.hashed_password)
    if not user_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user_db["id"])})
    refresh_token = create_refresh_token({"sub": str(user_db["id"])})
    response = JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    })
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return response

@router.post("/refresh_token")
@limiter.limit("30/minute")  # More lenient for token refresh
async def refresh_token(request: Request, request_data: RefreshTokenRequest):
    try:
        # Decode the refresh token
        payload = decode_refresh_token(request_data.refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Generate a new access token
        new_access_token = create_access_token({"sub": user_id})
        return {"access_token": new_access_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
@router.post("/logout")
async def logout():
    # Note: Without database-based token blacklisting, we rely on token expiration
    # For better security in production, consider using Redis or another in-memory store for blacklisting
    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie(key="refresh_token")
    return response