from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, RegistrationMessage, LoginRequest
from app.services.auth_service import AuthService
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_refresh_token
import jwt
from app.db.session import get_db
from app.schemas.token import RefreshTokenRequest
from fastapi.responses import JSONResponse
from app.services.token_blacklist_service import blacklist_token
from app.services.token_blacklist_service import is_token_blacklisted
from fastapi import Header

router = APIRouter()

@router.post("/register", response_model=RegistrationMessage, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.register_user(user)

@router.post("/login")
async def login_user(credentials: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user_db = auth_service.authenticate_user(credentials.email, credentials.hashed_password)
    if not user_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user_db.id)})
    refresh_token = create_refresh_token({"sub": str(user_db.id)})
    response = JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    })
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return response

@router.post("/refresh_token")
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        # Decode the refresh token
        payload = decode_refresh_token(request.refresh_token)
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
async def logout(authorization: str = Header(...), db: Session = Depends(get_db)):
    # Extract token from "Bearer <token>"
    token = authorization.replace("Bearer ", "")
    blacklist_token(db, token)
    response = JSONResponse({"message": "Logged out successfully"})
    return response